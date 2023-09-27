import logging
import subprocess
from pathlib import Path

import requests
from rich import print

from fly_audio_transcoder_worker import API_URL, JOB_ID


def get_job_details():
    r = requests.get(f"{API_URL}/jobs/{JOB_ID}/")
    return r.json()


def mark_job_as_complete():
    return


def transcode_audio_file(
    input_file: Path,
    output_file: Path,
    target_bit_rate: int,
    target_sample_rate: int,
):
    """
    Transcode the audio file to the target format.
    """
    command = [
        "ffmpeg",
        "-i",
        str(input_file),
        "-b:a",
        f"{target_bit_rate}k",
        "-ar",
        str(target_sample_rate),
        "-acodec",
        "libmp3lame",
        str(output_file),
    ]

    print(f"Triggering ffmpeg with this command: {command}")

    subprocess.run(command)
    return


def download_source_audio_file(
    download_url: str,
    destination_path: Path,
):
    """
    Download the source file to local disk.
    """
    r = requests.get(download_url)

    with open(destination_path, "wb") as audio_file:
        audio_file.write(r.content)

    return


def is_wave_file(
    audio_file: Path,
):
    with open(audio_file, "rb") as audio_file:
        riff = audio_file.read(4).decode("ascii")
        _ = audio_file.read(4)  # Read and discard the next 4 bytes (file size)
        wave = audio_file.read(4).decode("ascii")
        return riff == "RIFF" and wave == "WAVE"


def add_extension_to_source_audio_file(
    audio_file: Path,
):
    if is_wave_file(audio_file):
        target_path = f"/tmp/{audio_file.stem}.wav"
    audio_file.rename(target_path)
    return target_path


def upload_transcoded_audio_file(
    upload_url: str,
):
    return
