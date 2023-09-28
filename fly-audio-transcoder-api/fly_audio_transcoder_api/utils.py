import aioboto3
from botocore.config import Config

from fly_audio_transcoder_api import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
    S3_ENDPOINT_URL,
)


async def generate_presigned_s3_upload_url(
    object_key: str,
    content_disposition: str,
    content_type: str,
    expires_in: int = 3600,
):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=S3_ENDPOINT_URL,
        config=Config(
            signature_version="v4",
        ),
    ) as s3:
        r = await s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": S3_BUCKET_NAME,
                "Key": object_key,
                "ContentDisposition": content_disposition,
                "ContentType": content_type,
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
        config=Config(
            signature_version="v4",
        ),
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
