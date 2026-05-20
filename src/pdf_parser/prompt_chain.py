"""Sequential P1–P6 Claude API prompt chain for program criteria extraction."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 2.0

P1_SYSTEM = (
    "You are an expert in USDA agricultural grant programs. Extract information "
    "precisely from the provided document. Do not infer, assume, or add information "
    "not present in the text."
)

PROMPTS: list[tuple[str, str, str | None]] = [
    (
        "p1",
        P1_SYSTEM,
        "List every eligibility requirement a producer must meet to qualify for this "
        "program. Include all criteria — producer type, geographic requirements, loss "
        "type, disaster event requirements, insurance or conservation linkage "
        "requirements, and administrative or documentation requirements. Be "
        "exhaustive. Cite the document directly where possible. Return as a numbered list.",
    ),
    (
        "p2",
        None,
        "Based on the program document and the eligibility requirements identified, "
        "list all categories of producers who are explicitly excluded or ineligible. "
        "For each, state the specific condition that triggers exclusion. Return as a "
        "numbered list.",
    ),
    (
        "p3",
        None,
        "For each requirement from the eligibility list, classify it as either:\n"
        "(a) HARD PASS/FAIL — the producer either qualifies or they do not, regardless "
        "of degree\n"
        "(b) VARIABLE FACTOR — affects the size or likelihood of payment but does not "
        "alone disqualify\n"
        "Separate your response into two clearly labeled sections.",
    ),
    (
        "p4",
        None,
        "For each eligibility criterion and variable factor identified, name the specific "
        "data field that would be needed to verify it in a CRM or farm record system. "
        "Use lowercase_snake_case field names. Return a structured list: criterion → "
        "field name(s).",
    ),
    (
        "p5",
        None,
        "For the variable factors only, assign each to one of three tiers:\n"
        "Tier 1 — Strong indicator: primary driver of qualification or high payment "
        "potential\n"
        "Tier 2 — Moderate indicator: significantly influences payment size or likelihood\n"
        "Tier 3 — Supporting detail: administrative requirement; not a meaningful "
        "ranking signal\n"
        "For each assignment, provide a one-sentence rationale.",
    ),
    (
        "p6",
        None,
        "Based on everything extracted, describe in 3–5 plain-language sentences the "
        "ideal producer profile that would be the strongest possible match for this "
        "program — what they farm, where they are located, what happened to them, and "
        "what documentation they would already have.",
    ),
]


@dataclass
class PromptChainResult:
    p1: str
    p2: str
    p3: str
    p4: str
    p5: str
    p6: str

    def as_dict(self) -> dict[str, str]:
        return {
            "p1": self.p1,
            "p2": self.p2,
            "p3": self.p3,
            "p4": self.p4,
            "p5": self.p5,
            "p6": self.p6,
        }


def _is_retryable(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    message = str(exc).lower()
    retry_signals = ("rate", "timeout", "overloaded", "529", "503", "500")
    return any(signal in name or signal in message for signal in retry_signals)


def _call_with_retry(client: Any, **kwargs: Any) -> Any:
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            return client.messages.create(**kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt == MAX_RETRIES - 1 or not _is_retryable(exc):
                raise
            wait = INITIAL_BACKOFF_SECONDS * (2**attempt)
            logger.warning(
                "API call failed (attempt %s/%s), retrying in %.1fs: %s",
                attempt + 1,
                MAX_RETRIES,
                wait,
                exc,
            )
            time.sleep(wait)
    raise last_exc  # type: ignore[misc]


def _build_user_content(
    program_text: str,
    instruction: str,
    prior_outputs: list[str],
    cache_document: bool,
) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = []

    doc_block: dict[str, Any] = {
        "type": "text",
        "text": f"PROGRAM DOCUMENT:\n\n{program_text}",
    }
    if cache_document:
        doc_block["cache_control"] = {"type": "ephemeral"}
    content.append(doc_block)

    if prior_outputs:
        prior_text = "\n\n".join(
            f"--- Prior step {i + 1} ---\n{out}" for i, out in enumerate(prior_outputs)
        )
        content.append(
            {
                "type": "text",
                "text": f"PRIOR EXTRACTION OUTPUTS:\n\n{prior_text}",
            }
        )

    content.append({"type": "text", "text": instruction})
    return content


def _log_usage(step: str, response: Any) -> None:
    usage = getattr(response, "usage", None)
    if usage is None:
        print(f"[{step}] completed (usage metadata unavailable)")
        return
    input_tokens = getattr(usage, "input_tokens", "?")
    output_tokens = getattr(usage, "output_tokens", "?")
    cache_read = getattr(usage, "cache_read_input_tokens", 0)
    cache_creation = getattr(usage, "cache_creation_input_tokens", 0)
    print(
        f"[{step}] completed — "
        f"input_tokens={input_tokens}, output_tokens={output_tokens}, "
        f"cache_read={cache_read}, cache_creation={cache_creation}"
    )


class PromptChain:
    """Runs the sequential P1–P6 extraction chain against Claude."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. Add it to your .env file."
            )

    def run(self, program_text: str) -> PromptChainResult:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            ) from exc

        client = anthropic.Anthropic(api_key=self.api_key)
        outputs: list[str] = []
        result: dict[str, str] = {}

        for idx, (step_key, system_prompt, user_instruction) in enumerate(PROMPTS):
            assert user_instruction is not None
            messages = [
                {
                    "role": "user",
                    "content": _build_user_content(
                        program_text=program_text,
                        instruction=user_instruction,
                        prior_outputs=outputs,
                        cache_document=True,
                    ),
                }
            ]

            kwargs: dict[str, Any] = {
                "model": MODEL,
                "max_tokens": MAX_TOKENS,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = _call_with_retry(client, **kwargs)
            text_blocks = [
                block.text
                for block in response.content
                if hasattr(block, "text")
            ]
            step_output = "\n".join(text_blocks).strip()
            if not step_output:
                raise RuntimeError(f"Empty response from Claude at step {step_key}")

            outputs.append(step_output)
            result[step_key] = step_output
            _log_usage(step_key.upper(), response)

        return PromptChainResult(**result)
