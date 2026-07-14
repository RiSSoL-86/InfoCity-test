from pathlib import Path

import pytest
from pydantic import ValidationError

from services.rag.loaders import CsvLoader
from services.rag.schemas import Pair


async def test_csv_loader_normalizes_and_deduplicates(
    tmp_path: Path,
) -> None:
    """Normalize values and remove duplicate question-answer pairs."""
    path = tmp_path / "questions.csv"
    path.write_text(
        'question,answer\n" How reset? "," Follow guide "\n'
        '"How   reset?","Follow guide"\n',
        encoding="utf-8",
    )

    pairs = await CsvLoader(path=path).load()

    assert len(pairs) == 1
    assert pairs[0].question == "How reset?"
    assert pairs[0].answer == "Follow guide"
    assert len(pairs[0].content_hash) == 64


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("answer,question\nanswer,question\n", "CSV columns must be"),
        ("question,answer\nquestion,\n", "must not be empty"),
        ("question,answer\n", "contains no question-answer pairs"),
    ],
)
async def test_csv_loader_rejects_invalid_content(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    """Reject malformed or empty CSV snapshots."""
    path = tmp_path / "questions.csv"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        await CsvLoader(path=path).load()


async def test_csv_loader_requires_existing_file(tmp_path: Path) -> None:
    """Reject a missing CSV file."""
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="Source file not found"):
        await CsvLoader(path=path).load()


def test_pair_rejects_invalid_hash() -> None:
    """Reject a pair whose content hash is not SHA-256."""
    with pytest.raises(ValidationError):
        Pair(question="Question", answer="Answer", content_hash="invalid")
