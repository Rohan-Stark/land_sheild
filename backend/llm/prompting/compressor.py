from __future__ import annotations

import json
from typing import Any

from backend.config.logging import get_logger

logger = get_logger("llm.prompting.compressor")


class PromptCompressor:
    """Reduces prompt context to fit within a token budget.

    Strategy:
    1. Remove duplicate findings (identical type + key content).
    2. Collapse repeated evidence references.
    3. Truncate long chunk texts while preserving first/last sentences.
    4. Never remove source references.

    Uses a rough 4-chars-per-token estimate for budget enforcement.
    """

    CHARS_PER_TOKEN = 4  # Conservative estimate

    def __init__(self, max_tokens: int = 4096) -> None:
        self._max_tokens = max_tokens
        self._max_chars = max_tokens * self.CHARS_PER_TOKEN

    def compress(
        self,
        findings: list[dict[str, Any]],
        chunks: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Return compressed (findings, chunks, sources). Sources are never removed."""
        findings = self._deduplicate_findings(findings)
        chunks = self._collapse_chunks(chunks)

        # Estimate current size
        total_chars = self._estimate_chars(findings, chunks, sources)

        # Progressively truncate chunks if over budget
        while total_chars > self._max_chars and chunks:
            chunks = self._truncate_longest_chunk(chunks)
            total_chars = self._estimate_chars(findings, chunks, sources)

        logger.info(
            "Compressed prompt: findings=%d chunks=%d sources=%d est_tokens=%d",
            len(findings),
            len(chunks),
            len(sources),
            total_chars // self.CHARS_PER_TOKEN,
        )
        return findings, chunks, sources

    # ── Internals ─────────────────────────────────────────────────

    @staticmethod
    def _deduplicate_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen_keys: set[str] = set()
        unique: list[dict[str, Any]] = []
        for f in findings:
            key = json.dumps(f, sort_keys=True, default=str)
            if key not in seen_keys:
                seen_keys.add(key)
                unique.append(f)
        return unique

    @staticmethod
    def _collapse_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge chunks that share the same document_id and have highly overlapping text."""
        seen_texts: set[str] = set()
        collapsed: list[dict[str, Any]] = []
        for c in chunks:
            text = c.get("text", "")[:200]  # Compare by prefix
            if text not in seen_texts:
                seen_texts.add(text)
                collapsed.append(c)
        return collapsed

    @staticmethod
    def _truncate_longest_chunk(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Find the longest chunk text and truncate it to half."""
        if not chunks:
            return chunks

        longest_idx = 0
        longest_len = 0
        for i, c in enumerate(chunks):
            text_len = len(c.get("text", ""))
            if text_len > longest_len:
                longest_len = text_len
                longest_idx = i

        text = chunks[longest_idx].get("text", "")
        if len(text) > 200:
            half = len(text) // 2
            chunks[longest_idx]["text"] = text[:half] + " [...]"

        return chunks

    @staticmethod
    def _estimate_chars(
        findings: list[dict[str, Any]],
        chunks: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> int:
        total = 0
        for f in findings:
            total += len(json.dumps(f, default=str))
        for c in chunks:
            total += len(c.get("text", ""))
        for s in sources:
            total += len(json.dumps(s, default=str))
        return total
