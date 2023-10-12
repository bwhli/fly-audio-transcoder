import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import sleep

import httpx
import pyperclip
import typer
from fly_audio_transcoder_cli.utils import (
    _create_job,
    _do,
    _get_job,
    _start_job,
    _upload_source,
)
from rich import print

API_URL = os.getenv(
    "API_URL",
    "https://fly-audio-transcoder-api.fly.dev",
)

app = typer.Typer()


@app.command()
def do(
    concurrency: int = typer.Option(
        1,
        "--concurrency",
        "-c",
    )
):
    with ThreadPoolExecutor(max_workers=concurrency + 1) as executor:
        results = [
            executor.submit(_do, "mp3", 16, 320, 44100, API_URL)
            for _ in range(concurrency)
        ]

    transcode_download_urls = []

    for result in results:
        print(result.result())

    return


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
    r = _create_job(
        target_format,
        target_bit_depth,
        target_bit_rate,
        target_sample_rate,
        api_url,
    )
    print(r.json()["data"])
    pyperclip.copy(f"fat upload-source {r.json()['data']['_id']} '{r.json()['data']['source']['upload_url']}' <PATH_TO_SOURCE_FILE>")  # fmt: skip
    return


@app.command()
def get_job(
    job_id: uuid.UUID = typer.Argument(
        ...,
    ),
    api_url: str = typer.Option(
        API_URL,
        show_default=True,
    ),
):
    """
    Returns information about a specific job.
    """
    r = _get_job(
        job_id,
        api_url,
    )
    print(r.json()["data"])
    return


@app.command()
def start_job(
    job_id: uuid.UUID = typer.Argument(
        ...,
    ),
    machine_size: str = typer.Option(
        "performance-2x",
        "--machine-size",
    ),
    api_url: str = typer.Option(
        API_URL,
        show_default=True,
    ),
):
    r = _start_job(
        job_id,
        machine_size,
        api_url,
    )
    print(r.json()["data"])
    pyperclip.copy(f"fat get-job {job_id}")
    return


@app.command()
def upload_source(
    job_id: uuid.UUID = typer.Argument(
        ...,
    ),
    upload_url: str = typer.Argument(
        ...,
    ),
    source_file: Path = typer.Argument(
        ...,
    ),
):
    r = _upload_source(
        job_id,
        upload_url,
        source_file,
    )
    if r.status_code == 200:
        print("Success! Your source file has been uploaded.")
        pyperclip.copy(f"fat start-job {job_id}")
    else:
        print(f"{r.status_code}: Something went wrong. Please try again.")
