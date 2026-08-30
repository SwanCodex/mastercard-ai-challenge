"""
injection_utils.py

Splices an attacker payload string into a piece of otherwise-legitimate
tool-output text, according to the injection-position conventions defined
in docs Track A §10.2 ("Injection position") /
Track_A_Threat_Model §9.2.
"""

from __future__ import annotations

Position = str  # "start" | "middle" | "end" | "metadata"


def splice(base_text: str, payload: str, position: Position = "end") -> str:
    """Insert `payload` into `base_text` at the requested position.

    - start:    payload appears before any legitimate content
    - middle:   payload appears after legitimate content, mid-document
                (breaks on a sentence boundary near the midpoint when
                possible, per §10.2 "in the middle")
    - end:      payload appears after all legitimate content (default -
                AgentDojo found end-of-output injections to be
                particularly effective)
    - metadata: payload appears as a non-visible-looking metadata comment,
                simulating hidden/low-visibility content (relevant to
                A09/A22 IBAN-swap style attacks)
    """
    if not payload:
        return base_text

    if position == "start":
        return f"{payload}\n\n{base_text}"

    if position == "middle":
        midpoint = len(base_text) // 2
        break_at = base_text.find(". ", midpoint)
        if break_at == -1:
            break_at = midpoint
        else:
            break_at += 2
        return f"{base_text[:break_at]}{payload}\n{base_text[break_at:]}"

    if position == "metadata":
        return f"{base_text}\n\n<!-- metadata: {payload} -->"

    # default / "end"
    return f"{base_text}\n\n{payload}"
