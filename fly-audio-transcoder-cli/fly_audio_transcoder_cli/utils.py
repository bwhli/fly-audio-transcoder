from pathlib import Path
from time import sleep
from uuid import UUID

import httpx

ROOT_DIR = Path(__file__).parent.parent


def _create_job(
    target_format: str,
    target_bit_depth: int,
    target_bit_rate: int,
    target_sample_rate: int,
    api_url: str,
):
    payload = {
        "transcode": {
            "format": {
                "extension": target_format,
                "bit_depth": target_bit_depth,
                "bit_rate": target_bit_rate,
                "sample_rate": target_sample_rate,
            }
        }
    }
    with httpx.Client(
        timeout=10,
    ) as client:
        r = client.post(
            f"{api_url}/jobs/",
            json=payload,
        )
    return r


def _get_job(
    job_id: UUID,
    api_url: str,
):
    with httpx.Client(
        timeout=10,
    ) as client:
        r = client.get(
            f"{api_url}/jobs/{job_id}/",
        )
    return r


def _start_job(
    job_id: UUID,
    machine_size: str,
    api_url: str,
):
    with httpx.Client(
        timeout=10,
    ) as client:
        r = client.post(
            f"{api_url}/jobs/{job_id}/status/started/?machine_size={machine_size}",
        )
    return r


def _upload_source(
    job_id: UUID,
    upload_url: str,
    source_file: Path,
):
    with open(source_file, "rb") as f:
        with httpx.Client(
            timeout=10,
        ) as client:
            headers = {
                "content-type": "audio/wav",
                "content-disposition": f"attachment;filename={job_id}.wav",
            }
            r = client.put(
                upload_url,
                headers=headers,
                data=f,
            )
    return r


def _do(
    target_format: str,
    target_bit_depth: int,
    target_bit_rate: int,
    target_sample_rate: int,
    api_url: str,
):
    job = _create_job(
        target_format,
        target_bit_depth,
        target_bit_rate,
        target_sample_rate,
        api_url,
    )

    job_id = UUID(job.json()["data"]["_id"])
    print(f"Created Job: {job_id}")

    _upload_source(
        job_id,
        job.json()["data"]["source"]["upload_url"],
        ROOT_DIR / "tests" / "test.wav",
    )
    print(f"Uploaded source file for Job {job_id}")

    job = _start_job(
        job_id,
        "performance-2x",
        api_url,
    )
    print(f"Started Job {job_id} on Machine {job.json()['data']['machine_id']}")

    while True:
        print(f"Checking Job {job_id} for transcode download URL...")
        job = _get_job(job_id, api_url)
        transcode_download_url = job.json()["data"]["transcode"]["download_url"]
        if transcode_download_url:
            return job_id, transcode_download_url
        else:
            print(f"Transcode download URL for {job_id} not ready yet. Trying again in 5s...")  # fmt: skip
            sleep(5)
            continue
