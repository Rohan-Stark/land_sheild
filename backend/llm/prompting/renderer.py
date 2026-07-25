from __future__ import annotations

import json
from typing import Any

from backend.config.logging import get_logger
from backend.llm.prompting.compressor import PromptCompressor
from backend.llm.prompting.templates import get_template
from backend.llm.schemas.prompt import PromptContext, PromptMessage, PromptRequest, PromptRole
from backend.llm.schemas.runtime import RuntimeConfig

logger = get_logger("llm.prompting.renderer")


class PromptRenderer:
    """Merges PromptContext + Template into a final PromptRequest ready for Ollama.

    Pipeline:
    1. Select the intent-specific template → system message.
    2. Compress findings/chunks/sources to fit token budget.
    3. Build user message from question + context block.
    4. Assemble PromptRequest.
    """

    def __init__(self, config: RuntimeConfig) -> None:
        self._config = config
        self._compressor = PromptCompressor(max_tokens=config.max_prompt_tokens)

    def render(
        self,
        context: PromptContext,
        intent: str,
        model: str | None = None,
        request_id: str = "",
        user_id: str = "",
        stream: bool = False,
    ) -> PromptRequest:
        # 1. System template
        system_text = get_template(intent)

        # 2. Compress context
        findings, chunks, sources = self._compressor.compress(
            context.agent_findings,
            context.retrieved_chunks,
            context.agent_sources,
        )

        # 3. Build user message
        user_text = self._build_user_message(context, findings, chunks, sources)

        # 4. Estimate tokens
        total_text = system_text + user_text
        token_estimate = len(total_text) // 4

        messages = [
            PromptMessage(role=PromptRole.SYSTEM, content=system_text),
            PromptMessage(role=PromptRole.USER, content=user_text),
        ]

        return PromptRequest(
            model=model or self._config.default_model,
            messages=messages,
            temperature=self._config.temperature,
            top_p=self._config.top_p,
            max_tokens=self._config.max_tokens,
            stream=stream,
            request_id=request_id,
            user_id=user_id,
            intent=intent,
            prompt_token_estimate=token_estimate,
        )

    # ── Internals ─────────────────────────────────────────────────

    @staticmethod
    def _build_user_message(
        context: PromptContext,
        findings: list[dict[str, Any]],
        chunks: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> str:
        parts: list[str] = []

        # User question
        parts.append(f"## User Question\n{context.user_question}")

        # Agent summary
        if context.agent_summary:
            parts.append(f"## Agent Analysis\n{context.agent_summary}")

        # Findings
        if findings:
            findings_text = json.dumps(findings, indent=2, default=str)
            parts.append(f"## Findings\n{findings_text}")

        # Retrieved context
        if chunks:
            chunk_texts = []
            for i, c in enumerate(chunks, 1):
                text = c.get("text", "")
                score = c.get("final_score", 0.0)
                chunk_texts.append(f"[Source {i} | Score: {score:.2f}]\n{text}")
            parts.append(f"## Retrieved Context\n" + "\n\n".join(chunk_texts))

        # Warnings
        if context.agent_warnings:
            parts.append(f"## Warnings\n" + "\n".join(f"- {w}" for w in context.agent_warnings))

        # Next actions
        if context.agent_next_actions:
            parts.append(
                f"## Suggested Actions\n"
                + "\n".join(f"- {a}" for a in context.agent_next_actions)
            )

        return "\n\n".join(parts)
