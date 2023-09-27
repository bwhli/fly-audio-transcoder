from pathlib import Path

import aioboto3

from fly_audio_transcoder_api import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
    S3_ENDPOINT_URL,
)


def upload_source_file(
    file_path: Path,
):

    return


async def upload_to_s3():
    async with aioboto3.client("s3"):
        pass
    return


async def generate_presigned_s3_upload_url(
    object_key: str,
    expires_in: int = 3600,
):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=S3_ENDPOINT_URL,
    ) as s3:
        r = await s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": S3_BUCKET_NAME,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )
    return r


async def generate_presigned_s3_download_url(
    object_key: str,
    expires_in: int = 3600,
):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=S3_ENDPOINT_URL,
    ) as s3:
        r = await s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3_BUCKET_NAME,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )
    return r
