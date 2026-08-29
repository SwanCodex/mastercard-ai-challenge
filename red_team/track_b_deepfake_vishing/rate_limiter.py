"""
rate_limiter.py (Track B)

Tiny shared limiter so both mock agents — which each make their own
client.models.generate_content() calls, sometimes 2-3 per single
scenario turn — stay under a free-tier Gemini requests-per-minute quota.

A delay only *between variants* (as run_track_b.py also applies) isn't
enough on its own: a single scenario can burn through several calls in
a few seconds with no gap between them. Call throttle() immediately
before every generate_content call and it will block just long enough
to stay under budget, no matter how many calls happen back-to-back.

Configure via SENTINEL_MAX_CALLS_PER_MINUTE (default 4 — one below the
observed free-tier cap of 5, to leave headroom for clock skew/latency).
"""

from __future__ import annotations

import os
import time
from collections import deque

_MAX_CALLS_PER_MINUTE = int(
    os.environ.get("SENTINEL_MAX_CALLS_PER_MINUTE", "4")
)
_WINDOW_SECONDS = 60.0

_call_timestamps: deque = deque()


def throttle() -> None:
    """
    Block, if needed, until making another API call would not exceed
    the configured calls-per-minute budget.
    """

    now = time.monotonic()

    while _call_timestamps and now - _call_timestamps[0] > _WINDOW_SECONDS:
        _call_timestamps.popleft()

    if len(_call_timestamps) >= _MAX_CALLS_PER_MINUTE:

        wait_seconds = (
            _WINDOW_SECONDS - (now - _call_timestamps[0]) + 0.5
        )

        if wait_seconds > 0:
            print(
                f"       [rate_limiter] pausing {wait_seconds:.1f}s to "
                f"stay under {_MAX_CALLS_PER_MINUTE} req/min..."
            )
            time.sleep(wait_seconds)

        now = time.monotonic()

        while (
            _call_timestamps
            and now - _call_timestamps[0] > _WINDOW_SECONDS
        ):
            _call_timestamps.popleft()

    _call_timestamps.append(time.monotonic())
