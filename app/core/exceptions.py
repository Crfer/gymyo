"""Custom exceptions for adaptive training engine."""


class ValidationError(ValueError):
    """Raised when domain validation fails."""


class InsufficientDataError(RuntimeError):
    """Raised when there is not enough data to make a deterministic decision."""
