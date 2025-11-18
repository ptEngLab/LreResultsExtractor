from lre_client.api.exceptions import LREAuthenticationError, LREAPIError
from lre_client.utils.common_utils import RunSummary, TablePrinter
from lre_client.utils.logger import get_logger
from lre_client.api.client import LREClient
from lre_client.data.results_store import ResultsStore

log = get_logger(__name__)





def process_results(store: ResultsStore) -> None:
    """Example function that uses the stored results."""
    log.info("Processing stored results...")

    if store.run_status:
        status = store.run_status.get('State')
        log.info(f"Current run status: {status}")

        if status == 'Completed':
            log.info("Run completed successfully!")
        elif status == 'Running':
            log.info("Run is still in progress...")

    log.info(f"Total hosts: {len(store.hosts)}")


def main():
    results_store = ResultsStore()

    try:
        with LREClient() as lre:

            run_status = lre.runs.get_run_status()
            results_store.update_run_status(run_status)

            summary = RunSummary(run_status, settings=lre.settings)
            rows = summary.build_rows()
            TablePrinter.print(rows)
            lgs = summary.get_lgs_list()
            log.info(f" LGs used {lgs}")

            lre.results.download_analyzed_result()
            results_info = lre.results.get_run_results()
            results_store.update_run_results(results_info)

            process_results(results_store)

    except LREAuthenticationError as auth_err:
        log.error("Authentication failed: %s", auth_err)
    except LREAPIError as api_err:
        log.error("API request error: %s", api_err)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
