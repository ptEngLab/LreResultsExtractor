from lre_client.api.exceptions import LREAuthenticationError, LREAPIError
from lre_client.utils.logger import get_logger
from lre_client.api.client import LREClient
from lre_client.data.results_store import ResultsStore

log = get_logger(__name__)

def main():
    # Create a results store to hold our data
    results_store = ResultsStore()

    try:
        with LREClient() as lre:

            # Get run status and store it
            run_status = lre.runs.get_run_status()
            results_store.update_run_status(run_status)

            # Log the status summary
            log.info(results_store.get_run_status_summary())

            results_info = lre.results.get_run_results()
            results_store.update_run_results(results_info)

            # Now you can pass results_store to other functions/classes
            process_results(results_store)

    except LREAuthenticationError as auth_err:
        log.error("Authentication failed: %s", auth_err)
    except LREAPIError as api_err:
        log.error("API request error: %s", api_err)
    except Exception as e:
        log.error("Unexpected error: %s", e)

def process_results(store: ResultsStore) -> None:
    """Example function that uses the stored results."""
    log.info("Processing stored results...")

    # Access the stored run status
    if store.run_status:
        status = store.run_status.get('State')
        log.info(f"Current run status: {status}")

        # You can add more processing logic here
        if status == 'Completed':
            log.info("Run completed successfully!")
        elif status == 'Running':
            log.info("Run is still in progress...")

    # Access stored hosts
    log.info(f"Total hosts: {len(store.hosts)}")

if __name__ == "__main__":
    main()