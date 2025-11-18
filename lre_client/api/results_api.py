import zipfile
from pathlib import Path
from typing import Optional

from lre_client.api.base_api import LREBaseAPI
from lre_client.api.endpoints import RUN_RESULTS_LIST, RESULT_DATA_DOWNLOAD
from lre_client.api.exceptions import LREAPIError
from lre_client.models.results import RunResultsCollection
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


def extract_result_data(zip_path: Path, extract_dir: Optional[Path] = None) -> Path:
    """Extract a downloaded zip result."""
    if not zip_path.exists():
        raise LREAPIError(f"Zip file not found: {zip_path}")

    if extract_dir is None:
        extract_dir = zip_path.parent / zip_path.stem

    extract_dir = Path(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Extracting {zip_path} to {extract_dir}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        log.info(f"Successfully extracted to {extract_dir}")
        return extract_dir
    except zipfile.BadZipFile as e:
        raise LREAPIError(f"Invalid zip file: {str(e)}")
    except Exception as e:
        raise LREAPIError(f"Failed to extract zip file: {str(e)}")


class LREResultsAPI:
    """Access LRE Results API with typed models."""

    def __init__(self, base_api: LREBaseAPI):
        self.api = base_api
        self.settings = base_api.settings

    def _build_results_list_url(self, run_id: int) -> str:
        return RUN_RESULTS_LIST.format(
            domain=self.settings.lre_domain,
            project=self.settings.lre_project,
            run_id=run_id
        )

    def _build_result_download_url(self, run_id: int, result_id: int) -> str:
        return RESULT_DATA_DOWNLOAD.format(
            domain=self.settings.lre_domain,
            project=self.settings.lre_project,
            run_id=run_id,
            result_id=result_id
        )

    def get_run_results(self, run_id: Optional[int] = None) -> RunResultsCollection:
        if run_id is None:
            run_id = getattr(self.settings, "lre_run_id", None)
            if not run_id:
                raise ValueError("Run ID not provided and not found in settings.")

        url = self._build_results_list_url(run_id)
        log.info(f"Fetching results for run {run_id}")
        response = self.api.get(url)
        if response.status_code != 200:
            raise LREAPIError(f"Failed to fetch run results: {response.text}")

        data = response.json()
        collection = RunResultsCollection.from_api_response(run_id, data)
        log.debug(f"Found {len(collection.results)} results for run {run_id}")
        return collection

    def download_result_data(self, result_id: int, run_id: Optional[int] = None,
                             output_path: Optional[Path] = None) -> Path:
        if run_id is None:
            run_id = getattr(self.settings, "lre_run_id", None)
            if not run_id:
                raise ValueError("Run ID not provided and not found in settings.")

        url = self._build_result_download_url(run_id, result_id)

        if output_path is None:
            output_dir = Path.cwd() / "lre_results"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"Results_{run_id}.zip"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        log.info(f"Downloading result data for result {result_id} to {output_path}")

        try:
            response = self.api.get(url, stream=True)
            if response.status_code != 200:
                raise LREAPIError(f"Failed to download result data: {response.text}")

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            if output_path.exists() and output_path.stat().st_size > 0:
                log.info(f"Successfully downloaded result data to {output_path} ({output_path.stat().st_size} bytes)")
                return output_path
            else:
                raise LREAPIError("Downloaded file is empty or doesn't exist")
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise LREAPIError(f"Failed to download result data: {str(e)}")

    def download_analyzed_result(self, run_id: Optional[int] = None,
                                 output_path: Optional[Path] = None,
                                 extract: bool = False) -> Path:
        collection = self.get_run_results(run_id)
        result = collection.latest_analyzed
        if not result:
            raise LREAPIError(f"No analyzed result found for run {run_id or self.settings.lre_run_id}")

        zip_path = self.download_result_data(result.id, run_id, output_path)

        if extract:
            return extract_result_data(zip_path)

        return zip_path
