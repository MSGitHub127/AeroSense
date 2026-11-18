"""Domain-specific exception hierarchy for AeroSense."""
from __future__ import annotations


class AeroSenseBaseException(Exception):
    """Base exception class for all AeroSense application errors."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ProfileNotFoundError(AeroSenseBaseException):
    """Raised when a requested family air profile cannot be found."""

    def __init__(self, profile_id: str) -> None:
        super().__init__(f"Air quality profile with ID '{profile_id}' was not found.", status_code=404)
        self.profile_id = profile_id


class AQICalculationError(AeroSenseBaseException):
    """Raised when air quality index or particulate parameters violate physical limits."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)


class RecommendationGenerationError(AeroSenseBaseException):
    """Raised when routine or alternative recommendations cannot be formulated."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class SecurityValidationError(AeroSenseBaseException):
    """Raised when token or encryption verification fails."""

    def __init__(self, message: str = "Cryptographic security verification failed.") -> None:
        super().__init__(message, status_code=401)
