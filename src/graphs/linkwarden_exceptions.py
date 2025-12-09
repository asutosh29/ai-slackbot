class LinkwardenAPIError(Exception):
    """Base exception class for all Linkwarden API client errors."""
    pass

class LinkwardenAuthError(LinkwardenAPIError):
    """Raised for authentication or authorization errors (HTTP 401, 403)."""
    pass

class LinkwardenNotFoundError(LinkwardenAPIError):
    """Raised when a requested resource is not found (HTTP 404)."""
    pass

class LinkwardenServerError(LinkwardenAPIError):
    """Raised for server-side errors (HTTP 5xx)."""
    pass