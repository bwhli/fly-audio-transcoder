import os

from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
S3_ENDPOINT_URL = os.environ["S3_ENDPOINT_URL"]

DB_URL = os.environ["DB_URL"]

FLY_API_APP_NAME = os.environ["FLY_API_APP_NAME"]
FLY_API_TOKEN = os.environ["FLY_API_TOKEN"]
FLY_ORG_SLUG = os.environ["FLY_ORG_SLUG"]
FLY_WORKER_APP_NAME = os.environ["FLY_WORKER_APP_NAME"]
FLY_WORKER_IMAGE = os.environ["FLY_WORKER_IMAGE"]
