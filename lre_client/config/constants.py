from importlib import resources
from pathlib import Path

PACKAGE_ROOT: Path = resources.files("lre_client")
PROJECT_ROOT: Path = PACKAGE_ROOT.parent
ENV_FILE_PATH: Path = PROJECT_ROOT / "resources" / ".env"
