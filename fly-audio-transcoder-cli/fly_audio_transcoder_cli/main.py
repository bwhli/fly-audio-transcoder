import os
import uuid
from pathlib import Path

import httpx
import pyperclip
import typer
from rich import print

API_URL = os.getenv(
    "API_URL",
    "https://fly-audio-transcoder-api.fly.dev",
)

app = typer.Typer()


@app.command()
def create_job(
    target_format: str = typer.Option(
        "mp3",
        "--format",
    ),
    target_bit_depth: int = typer.Option(
        16,
        "--bit-depth",
    ),
    target_bit_rate: int = typer.Option(
        320,
        "--bit-rate",
    ),
    target_sample_rate: int = typer.Option(
        44100,
        "--sample-rate",
    ),
    api_url: str = typer.Option(
        API_URL,
        show_default=True,
    ),
):
    """
    Create a new transcoding job.
    """
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

    print(r.json()["data"])
    pyperclip.copy(f"fat upload-source {r.json()['data']['_id']} '{r.json()['data']['source']['upload_url']}' <PATH_TO_SOURCE_FILE>")  # fmt: skip

    return


@app.command()
def get_job(
    job_id: uuid.UUID = typer.Argument(...),
    api_url: str = typer.Option(
        API_URL,
        show_default=True,
    ),
):
    """
    Returns information about a specific job.
    """
    with httpx.Client(
        timeout=10,
    ) as client:
        r = client.get(
            f"{api_url}/jobs/{job_id}/",
        )

    print(r.json()["data"])

    return


@app.command()
def start_job(
    job_id: uuid.UUID = typer.Argument(...),
    api_url: str = typer.Option(
        API_URL,
        show_default=True,
    ),
):
    with httpx.Client(
        timeout=10,
    ) as client:
        r = client.post(
            f"{api_url}/jobs/{job_id}/status/started/",
        )

    print(r.json()["data"])
    pyperclip.copy(f"fat get-job {job_id}")

    return


@app.command()
def upload_source(
    job_id: uuid.UUID = typer.Argument(...),
    upload_url: str = typer.Argument(...),
    source_file: Path = typer.Argument(...),
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

    if r.status_code == 200:
        print("Success! Your source file has been uploaded.")
        pyperclip.copy(f"fat start-job {job_id}")
    else:
        print(f"{r.status_code}: Something went wrong. Please try again.")
