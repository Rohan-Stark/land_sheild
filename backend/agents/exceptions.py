from __future__ import annotations


class AgentBaseException(Exception):
    """Base exception for all agent-related errors."""
    pass


class AgentValidationError(AgentBaseException):
    """Raised when an agent's input context fails validation."""
    pass


class RetrievalError(AgentBaseException):
    """Raised when the retrieval service fails to fetch context."""
    pass


class ToolExecutionError(AgentBaseException):
    """Raised when a tool execution fails catastrophically."""
    pass


class ToolUnavailable(AgentBaseException):
    """Raised when a required tool is not available in the executor."""
    pass


class PropertyNotFound(AgentBaseException):
    """Raised when a specified property ID does not exist or is inaccessible."""
    pass


class DocumentNotFound(AgentBaseException):
    """Raised when a specified document does not exist."""
    pass


class OCRFailure(AgentBaseException):
    """Raised when document OCR fails during processing or retrieval."""
    pass
