from pydantic import BaseModel, ConfigDict, Field


class SearchInput(BaseModel):
    """Validate a semantic search query."""

    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=2000)


class AnswerItem(BaseModel):
    """Represent one semantic search result."""

    model_config = ConfigDict(from_attributes=True)

    question: str
    answer: str
