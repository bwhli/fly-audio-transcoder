import uuid

from fastapi import status
from fastapi.exceptions import HTTPException

from fly_audio_transcoder_api.models import Job


async def get_job_from_db(
    job_id: uuid.UUID,
) -> Job:
    job = await Job.get(job_id)
    if job:
        return job
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found.",
        )


async def get_all_jobs_from_db() -> list[Job]:
    jobs = await Job.find_all().to_list()
    print(jobs)
    return jobs
