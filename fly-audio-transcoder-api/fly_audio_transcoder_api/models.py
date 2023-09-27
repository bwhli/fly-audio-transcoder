import uuid

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class AudioFormat(BaseModel):
    extension: str
    bit_depth: int
    bit_rate: int
    sample_rate: int


class Source(BaseModel):
    download_url: str | None = None
    upload_url: str | None = None


class Transcode(BaseModel):
    format: AudioFormat
    download_url: str | None = None
    upload_url: str | None = None


class Job(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: Indexed(str) = "created"
    machine_id: Indexed(str) | None = None
    source: Source = Source()
    transcode: Transcode

    class Settings:
        name = "jobs"
