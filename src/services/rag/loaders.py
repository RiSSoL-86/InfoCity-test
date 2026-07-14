import csv
import io
from hashlib import sha256
from pathlib import Path

import aiofiles

from services.rag.schemas import Pair


class CsvLoader:
    """Read, validate and deduplicate question-answer pairs."""

    def __init__(self, path: Path) -> None:
        """Configure the source CSV path."""
        self.path = path

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize whitespace in a CSV value."""
        return " ".join(value.split())

    @staticmethod
    def _build_hash(question: str, answer: str) -> str:
        """Build a stable hash for a question-answer pair."""
        content = f"{question}\x1f{answer}".encode()
        return sha256(content).hexdigest()

    async def load(self) -> list[Pair]:
        """Load the current CSV snapshot."""
        if not self.path.is_file():
            raise FileNotFoundError(
                f"Source file not found: {self.path}",
            )

        async with aiofiles.open(
            self.path,
            encoding="utf-8-sig",
            newline="",
        ) as file:
            content = await file.read()

        reader = csv.DictReader(io.StringIO(content))
        if reader.fieldnames != ["question", "answer"]:
            raise ValueError("CSV columns must be: question, answer")

        pairs: dict[str, Pair] = {}
        for row_number, row in enumerate(reader, start=2):
            question = self._normalize(value=row.get("question") or "")
            answer = self._normalize(value=row.get("answer") or "")
            if not question or not answer:
                raise ValueError(
                    "Question and answer must not be empty "
                    f"at row {row_number}",
                )

            content_hash = self._build_hash(
                question=question,
                answer=answer,
            )
            pairs[content_hash] = Pair(
                question=question,
                answer=answer,
                content_hash=content_hash,
            )

        if not pairs:
            raise ValueError("CSV file contains no question-answer pairs")
        return list(pairs.values())
