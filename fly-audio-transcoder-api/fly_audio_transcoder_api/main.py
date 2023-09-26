import uuid

from fastapi import FastAPI

from fly_audio_transcoder_api.models import AudioFile, Job, TranscodeRequest

app = FastAPI()


@app.post("/jobs/")
async def create_job():
    job = Job()
    await job.save()

    return {
        "data": {
            "job": job,
        }
    }


@app.get("/jobs/{job_id}/upload/")
async def create_upload_url(
    job_id: uuid.UUID,
):
    upload_url = ""

    return {
        "data": {
            "upload_url": upload_url,
        }
    }


@app.post("/upload/")
async def upload_audio_file():
    return


@app.post("/transcode/")
async def transcode_audio_file():
    return
