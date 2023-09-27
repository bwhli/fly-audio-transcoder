import logging
import os
import wave
from pathlib import Path

import requests
from pydantic import BaseModel
from rich import print

from fly_audio_transcoder_worker import API_URL, JOB_ID
from fly_audio_transcoder_worker.models import AudioFormat
from fly_audio_transcoder_worker.utils import (
    add_extension_to_source_audio_file,
    download_source_audio_file,
    get_job_details,
    transcode_audio_file,
)


def main():
    job = get_job_details()

    print(job)

    # print(job)
    download_url = "https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav"

    # Download the source audio file to /tmp/{JOB_ID}
    download_source_audio_file(download_url, f"/tmp/{JOB_ID}")

    # Add a file extension to the source file.
    source_audio_file_with_extension = add_extension_to_source_audio_file(
        Path(f"/tmp/{JOB_ID}")
    )

    # Transcode the audio file!
    target_extension = job["data"]["transcode"]["format"]["extension"]
    target_bit_rate = job["data"]["transcode"]["format"]["bit_rate"]
    target_sample_rate = job["data"]["transcode"]["format"]["sample_rate"]

    transcode_audio_file(
        source_audio_file_with_extension,
        f"/tmp/{JOB_ID}.{target_extension}",
        target_bit_rate,
        target_sample_rate,
    )

    return


if __name__ == "__main__":
    main()
