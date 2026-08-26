"""Claude synthesis of precedent from similar past staff cases."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import anthropic

logger = logging.getLogger("precedent.synthesis")

_MODEL = "claude-sonnet-5"
_NO_MATCHES = "No similar past cases found. No precedent to apply, use judgment."
_RULES_PATH = Path(__file__).resolve().parent / "rules.txt"

_rules_text: str | None = None


def _load_rules() -> str:
    global _rules_text
    if _rules_text is None:
        try:
            _rules_text = _RULES_PATH.read_text(encoding="utf-8").strip()
        except OSError:
            logger.warning("rules.txt not found at %s; synthesizing without ruleset", _RULES_PATH)
            _rules_text = ""
    return _rules_text


class SynthesisError(RuntimeError):
    """Raised when Claude could not produce a synthesis."""


def _format_case(index: int, match: dict[str, Any]) -> str:
    distance = match.get("distance")
    header = f"Case {index + 1}"
    if isinstance(distance, (int, float)):
        header += f" (similarity distance {distance:.3f})"
    return (
        f"{header}:\n"
        f"Summary: {match.get('summary', '')}\n"
        f"Rule: {match.get('rule', '')}\n"
        f"Ruling: {match.get('ruling', '')}\n"
        f"Punishment: {match.get('punishment', '')}"
    )


def synthesize(query: str, matches: list[dict[str, Any]]) -> str:
    if not matches:
        return _NO_MATCHES

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise SynthesisError("ANTHROPIC_API_KEY is not set")

    cases_text = "\n\n".join(_format_case(i, m) for i, m in enumerate(matches))
    rules_text = _load_rules()
    system = (
        "You are helping Minecraft server staff apply consistent moderation "
        "precedent. Given a new case and the most similar past cases, write a "
        "short (3-5 sentence) summary of what precedent suggests for the new "
        "case, noting any relevant differences. When a relevant rule number "
        "exists in the ruleset below, cite it correctly instead of trusting "
        "whatever rule number staff typed on the past case. Do not invent "
        "facts not given. You are advisory only, staff make the final ruling. "
        "Never use an em dash (—) anywhere in your response; use a comma, "
        "period, or parentheses instead."
    )
    if rules_text:
        system += f"\n\nServer ruleset:\n{rules_text}"
    prompt = f"New case:\n{query}\n\nSimilar past cases:\n{cases_text}"
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=_MODEL,
            max_tokens=400,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": "low"},
        )
    except anthropic.APIError as e:
        raise SynthesisError(f"Claude request failed: {e}") from e

    parts = [
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ]
    text = "\n".join(parts).strip() or "(empty response)"
    return text.replace("—", ", ").replace("–", "-")
