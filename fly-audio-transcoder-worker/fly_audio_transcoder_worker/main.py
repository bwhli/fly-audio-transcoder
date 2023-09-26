import os
from pathlib import Path

import requests
from rich import print

from fly_audio_transcoder_worker import API_URL, JOB_ID


def get_job_details():
    r = requests.get(f"{API_URL}/jobs/{JOB_ID}/")
    return r.json()


def mark_job_as_complete():
    return


def transcode_audio_file():
    return


def download_source_audio_file():
    return


def upload_transcoded_audio_file():
    return


def main():
    job = get_job_details()
    print(job)
    return


if __name__ == "__main__":
    main()
