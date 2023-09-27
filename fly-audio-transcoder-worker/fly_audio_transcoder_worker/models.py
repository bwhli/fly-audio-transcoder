from pydantic import BaseModel


class AudioFormat(BaseModel):
    extension: str
    bit_depth: int
    bit_rate: int
    sample_rate: int
