import json
import os
import uuid
from pathlib import Path

import httpx
import typer
from rich import print

API_URL = os.getenv(
    "API_URL",
    "https://fly-audio-transcoder-api.fly.dev",
)

app = typer.Typer()


@app.command()
def create_job(
    api_url: str = typer.Option(
        API_URL,
        help="API URL",
        envvar="API_URL",
        show_default=True,
    )
):
    """
    Create a new transcoding job.
    """
    payload = {
        "transcode": {
            "format": {
                "extension": "mp3",
                "bit_depth": 16,
                "bit_rate": 256,
                "sample_rate": 44100,
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

    print(json.dumps(r.json()["data"], indent=4))

    return


@app.command()
def get_job(
    job_id: uuid.UUID = typer.Argument(...),
    api_url: str = typer.Option(
        API_URL,
        help="API URL",
        envvar="API_URL",
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

    print(json.dumps(r.json()["data"], indent=4))

    return


@app.command()
def start_job(
    job_id: uuid.UUID = typer.Argument(...),
    api_url: str = typer.Option(
        API_URL,
        help="API URL",
        envvar="API_URL",
        show_default=True,
    ),
):
    with httpx.Client(
        timeout=10,
    ) as client:
        r = client.post(
            f"{api_url}/jobs/{job_id}/status/started/",
        )

    print(json.dumps(r.json()["data"], indent=4))

    return


@app.command()
def upload_source_file(
    job_id: uuid.UUID = typer.Argument(...),
    source_file: Path = typer.Argument(...),
    upload_url: str = typer.Argument(...),
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
    else:
        print(f"{r.status_code}: Something went wrong. Please try again.")
