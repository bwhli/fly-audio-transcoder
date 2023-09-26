import uuid

import motor
from beanie import init_beanie
from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fly_python_sdk.fly import Fly
from fly_python_sdk.models.machine import FlyMachine, FlyMachineConfig
from pydantic import BaseModel

from fly_audio_transcoder_api import (
    DB_URL,
    FLY_API_APP_NAME,
    FLY_API_TOKEN,
    FLY_ORG_SLUG,
    FLY_WORKER_APP_NAME,
    FLY_WORKER_IMAGE,
)
from fly_audio_transcoder_api.models import Job, OutputFormat
from fly_audio_transcoder_api.utils import (
    generate_presigned_s3_download_url,
    generate_presigned_s3_upload_url,
)

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


@app.get("/jobs/")
async def get_jobs():
    jobs = await Job.find_all().to_list()
    return {
        "data": jobs,
    }


@app.get("/jobs/{job_id}/")
async def get_job(
    job_id: uuid.UUID,
):
    job = await Job.get(job_id)
    return {
        "data": job,
    }


class CreateJobRequest(BaseModel):
    output_formats: list[OutputFormat] = []


@app.post("/jobs/")
async def create_job(
    data: CreateJobRequest,
):
    """
    Create a new transcoding job.

    Args:
        output_formats (list[OutputFormat]): A list of output formats to transcode the source file to.
    """
    if len(data.output_formats) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide at least one output format.",
        )

    # Instantiate a new Job object.
    job = Job()

    # Create a presigned URL based on Job ID.
    # Use the object's UUID as the S3 object key because we don't know the image file name and format yet.
    job.upload_url = await generate_presigned_s3_upload_url(
        object_key=f"{job.id}/source.file",
    )

    # Set the output formats.
    job.output_formats = data.output_formats

    # Save the job to the db.
    await job.save()

    return {
        "data": job,
    }


@app.get("/jobs/{job_id}/upload/")
async def create_upload_url(
    job_id: uuid.UUID,
):
    upload_url = ""

    return {
        "data": upload_url,
    }


@app.post("/upload/")
async def upload_audio_file():
    return


@app.post("/jobs/{job_id}/transcode/")
async def transcode_audio_file(
    job_id: uuid.UUID,
):
    # Fetch job from db.
    job = await Job.get(job_id)

    # Create Machine environment.
    machine_env = {
        "API_URL": f"http://{FLY_API_APP_NAME}.flycast",
        "JOB_ID": f"{job.id}",
    }

    # Create Fly Machine config to pass to FlyMachine object.
    machine_config = FlyMachineConfig(
        env=machine_env,
        image=FLY_WORKER_IMAGE,
    )

    # Spin up a Fly Machine to transcode the audio file.
    worker_app = Fly(FLY_API_TOKEN).Org(FLY_ORG_SLUG).App(FLY_WORKER_APP_NAME)
    machine = await worker_app.create_machine(
        FlyMachine(name=job.id, config=machine_config),
    )

    # Store Machine ID in Job object.
    job.machine_id = machine.id

    # Generate a presigned URL to download the source file and store in db.
    job.download_url = await generate_presigned_s3_download_url(f"{job.id}/source.file")

    # Start the Machine.
    await machine.start()

    return {
        "data": job,
    }
