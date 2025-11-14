from pathlib import Path

# Single source of truth for project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = PROJECT_ROOT / "resources/.env"
