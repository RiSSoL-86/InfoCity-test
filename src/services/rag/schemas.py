from pydantic import BaseModel, ConfigDict, Field


class Pair(BaseModel):
    """One validated question-answer pair from a source file."""

    model_config = ConfigDict(frozen=True)

    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
