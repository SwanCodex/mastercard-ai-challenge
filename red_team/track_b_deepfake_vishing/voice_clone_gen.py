"""
voice_clone_gen.py

Track B audio-artifact generator.

ETHICS / SCOPE (read before running):

    This module only ever synthesizes speech using voices belonging to
    consenting team members, registered in CONSENTING_TEAM_VOICES below.
    It must NEVER be pointed at a real customer's or non-consenting
    person's voice. It exists to produce a demo-grade audio artifact
    showing "what an attacker's cloned-voice call might sound like" for
    the live pitch, not to build a general-purpose voice cloning tool.

    See docs/ethics_and_safety.md — get explicit team sign-off before
    generating any audio.

IMPLEMENTATION NOTE:

    True voice cloning (matching a specific consenting teammate's timbre)
    requires a reference-audio-conditioned TTS model (e.g. Coqui XTTS-v2,
    ElevenLabs voice cloning API). That is a heavier dependency than this
    11-day build needs for the round-trip demo to work end-to-end, so the
    default backend here is `edge-tts`: free, no API key, no GPU, and
    good enough to produce a realistic-sounding attacker call clip.

    Every artifact this module writes is tagged with backend="edge_tts"
    (a *stand-in* synthetic voice) rather than falsely claiming to be a
    verified clone of a specific teammate's voice. If your team later
    wires in a real reference-audio cloning backend, set
    SENTINEL_TTS_BACKEND=xtts (or elevenlabs) and implement
    `_synthesize_xtts` / `_synthesize_elevenlabs` below — the call sites
    in run_track_b.py do not need to change.
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Consent registry
# ---------------------------------------------------------------------------
#
# Only speaker_ids listed here (with consented=True) may be used. Anyone
# calling this module with an unregistered or non-consenting speaker_id
# gets a hard error, not a silent fallback.

CONSENTING_TEAM_VOICES: Dict[str, Dict[str, Any]] = {
    # Example entries — replace with your actual consenting teammates.
    # "edge_tts_voice" is a stock TTS voice used as a stand-in; it is
    # NOT a clone of that person's actual voice unless a real
    # reference-audio backend has been wired in (see module docstring).
    "teammate_a": {
        "consented": True,
        "display_name": "Person A (self, demo voice)",
        "edge_tts_voice": "en-IN-PrabhatNeural",
    },
    "teammate_b": {
        "consented": True,
        "display_name": "Person B (self, demo voice)",
        "edge_tts_voice": "en-IN-NeerjaNeural",
    },
}


class ConsentError(RuntimeError):
    pass


@dataclass
class SynthesisResult:
    audio_path: Optional[str]
    backend: str
    speaker_id: str
    consented: bool
    text: str


def _require_consent(speaker_id: str) -> Dict[str, Any]:
    entry = CONSENTING_TEAM_VOICES.get(speaker_id)

    if entry is None or not entry.get("consented"):
        raise ConsentError(
            f"speaker_id '{speaker_id}' is not a registered, consenting "
            "team voice. Add it to CONSENTING_TEAM_VOICES with "
            "consented=True before use. Never synthesize a real "
            "customer's or non-consenting person's voice."
        )

    return entry


async def _synthesize_edge_tts(
    text: str,
    edge_voice: str,
    output_path: str,
) -> None:
    import edge_tts  # optional dependency, see requirements note below

    communicate = edge_tts.Communicate(text=text, voice=edge_voice)
    await communicate.save(output_path)


def synthesize_clone(
    text: str,
    speaker_id: str,
    output_dir: str,
    file_stem: str,
) -> SynthesisResult:
    """
    Produce a demo call-audio artifact "spoken" by a consenting team
    member's stand-in TTS voice.

    Returns a SynthesisResult with audio_path=None (rather than raising)
    if the TTS backend is unavailable, so a missing optional dependency
    never blocks the rest of the Track B campaign — the attack is still
    scored on the transcript text either way.
    """

    entry = _require_consent(speaker_id)

    backend = os.environ.get("SENTINEL_TTS_BACKEND", "edge_tts")

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{file_stem}.mp3")

    if backend == "edge_tts":
        try:
            asyncio.run(
                _synthesize_edge_tts(
                    text=text,
                    edge_voice=entry["edge_tts_voice"],
                    output_path=output_path,
                )
            )
        except Exception as exc:  # pragma: no cover - optional dependency
            print(
                f"[voice_clone_gen] WARNING: TTS synthesis skipped "
                f"({exc}). Continuing without audio artifact."
            )
            output_path = None

    else:
        print(
            f"[voice_clone_gen] WARNING: unknown SENTINEL_TTS_BACKEND="
            f"'{backend}'. Continuing without audio artifact."
        )
        output_path = None

    result = SynthesisResult(
        audio_path=output_path,
        backend=backend,
        speaker_id=speaker_id,
        consented=True,
        text=text,
    )

    # Sidecar metadata makes clear, next to the audio file itself, that
    # this is a consented stand-in voice and not a clone of a real
    # customer or a non-consenting person.
    if output_path:
        meta_path = output_path.replace(".mp3", ".json")
        with open(meta_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "speaker_id": speaker_id,
                    "display_name": entry["display_name"],
                    "backend": backend,
                    "is_real_voice_clone": False,
                    "note": (
                        "Stand-in TTS voice used with this consenting "
                        "team member's permission for demo purposes. "
                        "Not a biometric clone of any real voice."
                    ),
                    "text": text,
                },
                handle,
                indent=2,
            )

    return result


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    demo = synthesize_clone(
        text=(
            "Hi, this is a demo vishing line used only for SENTINEL's "
            "own red-team testing."
        ),
        speaker_id="teammate_a",
        output_dir="logs/audio",
        file_stem="smoke_test",
    )

    print(demo)
