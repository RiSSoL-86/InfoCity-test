from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SRC_DIR.parent
ENV_FILE = SRC_DIR / ".env"
