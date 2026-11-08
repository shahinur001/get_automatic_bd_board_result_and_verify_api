class EBoardResultsError(Exception):
    """Base exception for eboardresults integration."""

class EBoardConnectionError(EBoardResultsError):
    """Raised when the external website cannot be reached."""

class EBoardResponseError(EBoardResultsError):
    """Raised when the external website returns an unexpected response."""


class EBoardAccessError(EBoardResultsError):
    """Raised when access is denied or requires additional verification."""