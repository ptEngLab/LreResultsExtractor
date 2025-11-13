# lre_client/api/exceptions.py

class LREError(Exception):
    """Base exception for LRE client errors."""
    pass


class LREConnectionError(LREError):
    """Raised when connection to LRE server fails."""
    pass


class LREAuthenticationError(LREError):
    """Raised when authentication fails."""
    pass


class LREAPIError(LREError):
    """Raised when API returns an error."""
    pass
