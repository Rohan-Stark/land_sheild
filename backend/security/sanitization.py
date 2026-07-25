from __future__ import annotations

import re


class InputSanitizer:
    """Removes potentially dangerous payloads from user inputs."""

    # Strip HTML tags
    HTML_REGEX = re.compile(r"<[^>]*>")
    
    # Strip carriage returns and line feeds to prevent log injection
    LOG_INJECTION_REGEX = re.compile(r"[\r\n]")

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize plain text inputs (e.g., search queries, prompt inputs)."""
        if not text:
            return text
            
        clean = InputSanitizer.HTML_REGEX.sub("", text)
        clean = InputSanitizer.LOG_INJECTION_REGEX.sub(" ", clean)
        return clean.strip()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Keep only safe characters in uploaded filenames."""
        if not filename:
            return "unnamed_file"
        
        # Keep alphanumeric, dots, dashes, underscores
        safe = re.sub(r"[^a-zA-Z0-9.\-_]", "_", filename)
        return safe.strip("_")
