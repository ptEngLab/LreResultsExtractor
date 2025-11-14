import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any

from lre_client.api.base_api import LREBaseAPI
from lre_client.api.endpoints import RUN_RESULTS_LIST, RESULT_DATA_DOWNLOAD
from lre_client.api.exceptions import LREAPIError
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


def extract_result_data(zip_path: Path, extract_dir: Optional[Path] = None) -> Path:
    """
    Extract downloaded result zip file.

    :param zip_path: Path to the zip file
    :param extract_dir: Optional extraction directory
    :return: Path to the extraction directory
    """
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
    """Provides access to LRE Results API for downloading analyzed results."""

    def __init__(self, base_api: LREBaseAPI):
        self.api = base_api
        self.settings = base_api.settings

    def _build_results_list_url(self, run_id: int) -> str:
        """Build URL for listing results of a run."""
        return RUN_RESULTS_LIST.format(
            domain=self.settings.lre_domain,
            project=self.settings.lre_project,
            run_id=run_id
        )

    def _build_result_download_url(self, run_id: int, result_id: int) -> str:
        """Build URL for downloading result data."""
        return RESULT_DATA_DOWNLOAD.format(
            domain=self.settings.lre_domain,
            project=self.settings.lre_project,
            run_id=run_id,
            result_id=result_id
        )

    def get_run_results(self, run_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get list of all results for a specific run.

        :param run_id: Run ID (uses settings if not provided)
        :return: List of result objects
        """
        if run_id is None:
            run_id = getattr(self.settings, "lre_run_id", None)
            if run_id is None or run_id == 0:
                raise ValueError("Run ID not provided and not found in settings.")

        url = self._build_results_list_url(run_id)

        log.info(f"Fetching results for run {run_id}")
        response = self.api.get(url)
        if response.status_code != 200:
            raise LREAPIError(f"Failed to fetch run results: {response.text}")

        results = response.json()
        log.info(f"Found {len(results)} results for run {run_id}")
        return results

    def get_analyzed_result_id(self, run_id: Optional[int] = None) -> Optional[int]:
        """
        Find the result ID for the analyzed result.

        :param run_id: Run ID (uses settings if not provided)
        :return: Result ID of analyzed result, or None if not found
        """
        results = self.get_run_results(run_id)

        for result in results:
            result_type = result.get('ResultType', '')
            # Look for analyzed results (case-insensitive)
            if 'ANALYZED' in result_type.upper():
                result_id = result.get('ID')
                result_name = result.get('Name', 'Unknown')
                log.info(f"Found analyzed result: ID={result_id}, Name='{result_name}', Type='{result_type}'")
                return result_id

        log.warning("No analyzed result found in the results list")
        return None

    def download_result_data(self, result_id: int, run_id: Optional[int] = None,
                             output_path: Optional[Path] = None) -> Path:
        """
        Download result data as zip file.

        :param result_id: Result ID to download
        :param run_id: Run ID (uses settings if not provided)
        :param output_path: Optional output path for the zip file
        :return: Path to the downloaded zip file
        """
        if run_id is None:
            run_id = getattr(self.settings, "lre_run_id", None)
            if run_id is None or run_id == 0:
                raise ValueError("Run ID not provided and not found in settings.")

        url = self._build_result_download_url(run_id, result_id)

        # Set default output path if not provided
        if output_path is None:
            output_dir = Path.cwd() / "lre_results"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"run_{run_id}_result_{result_id}.zip"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        log.info(f"Downloading result data for result {result_id} to {output_path}")

        try:
            # Stream the download to handle large files
            response = self.api.get(url, stream=True)
            if response.status_code != 200:
                raise LREAPIError(f"Failed to download result data: {response.text}")

            # Write the content to file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Verify the file was downloaded
            if output_path.exists() and output_path.stat().st_size > 0:
                log.info(f"Successfully downloaded result data to {output_path} ({output_path.stat().st_size} bytes)")
                return output_path
            else:
                raise LREAPIError("Downloaded file is empty or doesn't exist")

        except Exception as e:
            # Clean up partially downloaded file
            if output_path.exists():
                output_path.unlink()
            raise LREAPIError(f"Failed to download result data: {str(e)}")

    def download_analyzed_result(self, run_id: Optional[int] = None,
                                 output_path: Optional[Path] = None,
                                 extract: bool = False) -> Path:
        """
        Complete workflow: find analyzed result and download it.

        :param run_id: Run ID (uses settings if not provided)
        :param output_path: Optional output path for the zip file
        :param extract: Whether to extract the zip file after download
        :return: Path to the downloaded file or extraction directory
        """
        if run_id is None:
            run_id = getattr(self.settings, "lre_run_id", None)
            if run_id is None or run_id == 0:
                raise ValueError("Run ID not provided and not found in settings.")

        log.info(f"Starting analyzed result download for run {run_id}")

        # Step 1: Find analyzed result ID
        result_id = self.get_analyzed_result_id(run_id)
        if result_id is None:
            raise LREAPIError(f"No analyzed result found for run {run_id}")

        # Step 2: Download result data
        zip_path = self.download_result_data(result_id, run_id, output_path)

        # Step 3: Extract if requested
        if extract:
            extract_dir = extract_result_data(zip_path)
            return extract_dir

        return zip_path

    def get_result_info(self, run_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get information about all results for a run, highlighting analyzed results.

        :param run_id: Run ID (uses settings if not provided)
        :return: Dictionary with result information
        """
        results = self.get_run_results(run_id)

        analyzed_results = []
        other_results = []

        for result in results:
            result_info = {
                'id': result.get('ID'),
                'name': result.get('Name'),
                'type': result.get('ResultType'),
                'start_time': result.get('StartTime'),
                'duration': result.get('Duration'),
                'vusers': result.get('VusersCount')
            }

            if 'ANALYZED' in result.get('ResultType', '').upper():
                analyzed_results.append(result_info)
            else:
                other_results.append(result_info)

        return {
            'run_id': run_id or self.settings.lre_run_id,
            'analyzed_results': analyzed_results,
            'other_results': other_results,
            'total_results': len(results),
            'analyzed_count': len(analyzed_results)
        }