from pathlib import Path


from fly_audio_transcoder_worker import JOB_ID
from fly_audio_transcoder_worker.utils import (
    add_extension_to_source_audio_file,
    download_source_audio_file,
    get_job_details,
    mark_job_as_finished,
    transcode_audio_file,
    upload_transcoded_audio_file,
)


def main():
    job = get_job_details()

    # Download the source audio file to /tmp/{JOB_ID}
    download_source_audio_file(
        job["data"]["source"]["download_url"],
        Path(f"/tmp/{JOB_ID}"),
    )

    # Add a file extension to the source file.
    source_audio_file_with_extension = add_extension_to_source_audio_file(
        Path(f"/tmp/{JOB_ID}")
    )

    # Transcode the audio file!
    target_extension = job["data"]["transcode"]["format"]["extension"]
    target_bit_rate = job["data"]["transcode"]["format"]["bit_rate"]
    target_sample_rate = job["data"]["transcode"]["format"]["sample_rate"]

    output_file_path = Path(f"/tmp/{JOB_ID}.{target_extension}")

    transcode_audio_file(
        source_audio_file_with_extension,
        output_file_path,
        target_bit_rate,
        target_sample_rate,
    )

    upload_transcoded_audio_file(
        job["data"]["transcode"]["upload_url"],
        output_file_path,
    )

    mark_job_as_finished()

    return


if __name__ == "__main__":
    main()
