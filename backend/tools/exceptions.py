from __future__ import annotations


class ToolBaseException(Exception):
    """Base exception for all tool-related errors."""
    pass


class ToolPermissionError(ToolBaseException):
    """Raised when a user attempts to access data they do not own."""
    pass


class ToolValidationError(ToolBaseException):
    """Raised when tool inputs fail validation schemas."""
    pass


class ResourceNotFoundError(ToolBaseException):
    """Raised when the requested property, document, or alert is not found."""
    pass


class ExternalServiceError(ToolBaseException):
    """Raised when OCR, Database, or ChromaDB times out or fails."""
    pass


class ToolNotRegisteredError(ToolBaseException):
    """Raised when attempting to execute a tool that does not exist."""
    pass
