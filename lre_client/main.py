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
            # Get hosts and store them
            hosts = lre.hosts.list_hosts()
            results_store.update_hosts(hosts)

            # Log hosts information
            for host in results_store.hosts:
                log.info(f"Host: {host.get('Name')} (ID: {host.get('ID')})")

            # Get run status and store it
            run_status = lre.runs.get_run_status()
            results_store.update_run_status(run_status)

            # Log the status summary
            log.info(results_store.get_run_status_summary())

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
        status = store.run_status.get('status')
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