import asyncio
import logging
from typing import Annotated

import motor
from beanie import init_beanie
from fastapi import Depends, FastAPI, HTTPException, status
from fly_audio_transcoder_api import (
    DB_URL,
    FLY_API_TOKEN,
    FLY_APP_NAME,
    FLY_ORG_SLUG,
    FLY_WORKER_APP_NAME,
    FLY_WORKER_IMAGE,
)
from fly_audio_transcoder_api.dependencies import get_all_jobs_from_db, get_job_from_db
from fly_audio_transcoder_api.models import Job, Transcode
from fly_audio_transcoder_api.utils import (
    generate_presigned_s3_download_url,
    generate_presigned_s3_upload_url,
)
from fly_python_sdk.fly import Fly
from fly_python_sdk.models.machine import (
    FlyMachine,
    FlyMachineConfig,
    FlyMachineConfigRestart,
)
from pydantic import BaseModel

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """
    Run startup tasks.
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
    await init_beanie(
        database=client["fly_audio_transcoder"],
        document_models=[Job],
    )


@app.delete("/jobs/")
async def delete_jobs(
    jobs: Annotated[
        list[Job],
        Depends(get_all_jobs_from_db),
    ]
) -> None:
    """
    Deletes all jobs in the database along with their associated Fly Machines.
    Useful for resetting the database for testing purposes.
    """
    if len(jobs) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No jobs found.",
        )

    async def _delete_job_and_machine(
        job: Job,
    ):
        if job.machine_id:
            machine = (
                Fly(FLY_API_TOKEN)
                .Org(FLY_ORG_SLUG)
                .App(FLY_WORKER_APP_NAME)
                .Machine(job.machine_id)
            )
            await machine.destroy()
            logging.info(f"Destroyed Machine {job.machine_id}.")

        await job.delete()

        return

    await asyncio.gather(*[_delete_job_and_machine(job) for job in jobs])

    return


@app.get("/jobs/")
async def get_jobs(
    jobs: Annotated[
        list[Job],
        Depends(get_all_jobs_from_db),
    ]
) -> dict[str, list[Job]]:
    """
    Returns a list of jobs in the database.
    """
    return {
        "data": jobs,
    }


class JobDetails(BaseModel):
    transcode: Transcode


@app.post("/jobs/")
async def create_job(
    job_details: JobDetails,
):
    """
    Create a new transcoding job.
    """
    # Instantiate a new Job object.
    job = Job(
        transcode=job_details.transcode,
    )

    # Create a presigned upload URL based on Job ID.
    job.source.upload_url = await generate_presigned_s3_upload_url(
        object_key=f"sources/{job.id}",
        content_disposition=f"attachment;filename={job.id}.wav",
        content_type="audio/wav",
        expires_in=86400,
    )

    # Save the job to the db.
    await job.save()

    return {
        "data": job,
    }


@app.get("/jobs/{job_id}/")
async def get_job(
    job: Annotated[
        Job,
        Depends(get_job_from_db),
    ],
):
    """
    Returns information about a specific job.
    """
    return {
        "data": job,
    }


@app.post("/jobs/{job_id}/status/started/")
async def update_job_status_to_started(
    job: Annotated[
        Job,
        Depends(get_job_from_db),
    ],
    machine_size: str = "performance-2x",
):
    """
    This endpoint creates a Fly Machine to transcode the audio file.
    """
    # Create Machine environment.
    machine_env = {
        "API_URL": f"http://{FLY_APP_NAME}.flycast",
        "JOB_ID": f"{job.id}",
    }

    # Create Fly Machine config to pass to FlyMachine object.
    machine_config = FlyMachineConfig(
        env=machine_env,
        image=FLY_WORKER_IMAGE,
        size=machine_size,
        auto_destroy=True,
        restart=FlyMachineConfigRestart(policy="no"),
    )

    # Generate a presigned URL to download the source file and store in db.
    # This URL is used by the Fly Machine to download the source file.
    job.source.download_url = await generate_presigned_s3_download_url(
        object_key=f"sources/{job.id}",
        expires_in=86400,
    )

    # Generate a presigned URL which can be used to upload the transcoded file.
    # This URL is used by the Fly Machine to upload the transcoded file.
    job.transcode.upload_url = await generate_presigned_s3_upload_url(
        object_key=f"transcodes/{job.id}.{job.transcode.format.extension}",
        content_disposition=f"attachment;filename={job.id}.mp3",
        content_type="audio/mpeg",
        expires_in=86400,
    )

    # Save generated URLs to db.
    await job.save()

    # Spin up a Fly Machine to transcode the audio file.
    worker_app = Fly(FLY_API_TOKEN).Org(FLY_ORG_SLUG).App(FLY_WORKER_APP_NAME)
    machine = await worker_app.create_machine(
        FlyMachine(name=str(job.id), config=machine_config),
    )

    # Store Machine ID in Job object.
    job.machine_id = machine.id

    # Set job status to "staged".
    job.status = "started"

    await job.save()

    return {
        "data": job,
    }


@app.post("/jobs/{job_id}/status/completed/")
async def update_job_status_to_completed(
    job: Annotated[
        Job,
        Depends(get_job_from_db),
    ],
):
    # Generate a presigned download URL for transcoded file.
    # This URL is used by the client to download the transcoded file.
    job.transcode.download_url = await generate_presigned_s3_download_url(
        object_key=f"transcodes/{job.id}.{job.transcode.format.extension}",
        expires_in=86400,
    )

    job.status = "completed"

    await job.save()

    return {
        "data": job,
    }
