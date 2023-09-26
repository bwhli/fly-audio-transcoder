import uuid

from beanie import Document, Field
from pydantic import BaseModel


class InputFormat(BaseModel):
    format: str
    bit_depth: int
    bit_rate: int
    sample_rate: int


class OutputFormat(BaseModel):
    format: str
    bit_depth: int
    bit_rate: int
    sample_rate: int


class Job(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: str
    machine_id: str | None = None
    file_name: str | None = None
    input_format: InputFormat | None = None
    output_formats: list[OutputFormat] | None = None

    class Settings:
        name = "jobs"
