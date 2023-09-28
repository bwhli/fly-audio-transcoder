from pathlib import Path

import httpx
from rich import print

API_URL = "https://fly-audio-transcoder-api.fly.dev"


def create_job():
    with httpx.Client(timeout=10) as client:
        body = {
            "transcode": {
                "format": {
                    "extension": "mp3",
                    "bit_depth": 16,
                    "bit_rate": 192,
                    "sample_rate": 44100,
                }
            }
        }
        r = client.post(f"{API_URL}/jobs/", json=body)

    assert r.status_code == 200
    return r.json()["data"]


def start_job(
    job_id: str,
):
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"{API_URL}/jobs/{job_id}/status/started/",
        )
        print(r.status_code)

    assert r.status_code == 200
    return r.json()["data"]


def upload_source_file_to_r2(
    upload_url: str,
    content_type: str,
    content_disposition: str,
):
    with open(Path(__file__).parent / "test.wav", "rb") as f:

        with httpx.Client() as client:
            headers = {
                "content-type": content_type,
                "content-disposition": content_disposition,
            }
            r = client.put(
                upload_url,
                headers=headers,
                data=f,
            )

        assert r.status_code == 200


def main():
    # Create a new job.
    job = create_job()
    print("A job has been created!")
    print(job)

    # Use the provided presigned URL to upload a WAV file.
    print(f"Uploading test audio file to R2...")
    upload_source_file_to_r2(
        upload_url=job["source"]["upload_url"],
        content_type="audio/wav",
        content_disposition=f"attachment;filename={job['_id']}.wav",
    )
    print(f"Upload successful!")

    # Stage the job.
    job = start_job(job["_id"])
    print("The job has been started!")
    print(job)

    return


if __name__ == "__main__":
    main()
