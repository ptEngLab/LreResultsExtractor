from lre_client.api.exceptions import LREAuthenticationError, LREAPIError
from lre_client.utils.logger import get_logger  # centralized logger
from lre_client.api.client import LREClient

log = get_logger(__name__)  # Use module-specific name


def main():
    # Using context manager ensures login/logout and session cleanup
    try:
        with LREClient() as lre:
            hosts = lre.hosts.list_hosts()  # Auto-login happens here
            for host in hosts:
                log.info(f"Host: {host.get('Name')} (ID: {host.get('ID')})")

            run_status = lre.runs.get_run_status()
            log.info(run_status)

    except LREAuthenticationError as auth_err:
        log.error("Authentication failed:", auth_err)
    except LREAPIError as api_err:
        log.error("API request error:", api_err)
    except Exception as e:
        log.error("Unexpected error: %s", e)



if __name__ == "__main__":
    main()
