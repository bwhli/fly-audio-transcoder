import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

API_URL = os.environ["API_URL"]
JOB_ID = os.environ["JOB_ID"]

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_ENDPOINT_URL = os.environ["S3_ENDPOINT_URL"]

SOURCE_FILE_PATH = Path()
