import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

API_URL = os.environ["API_URL"]
JOB_ID = os.environ["JOB_ID"]
