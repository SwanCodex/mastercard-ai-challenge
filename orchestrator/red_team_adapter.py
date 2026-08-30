import json
from pathlib import Path

from shared.schemas.attack_event import AttackEvent


def load_attack_events(path: str | Path) -> list[AttackEvent]:
    """
    Load Blue-Team-facing AttackEvents written by a Red Team campaign.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Attack event log not found: {path}"
        )

    events: list[AttackEvent] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
                events.append(AttackEvent.model_validate(data))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid AttackEvent at line {line_number} "
                    f"in {path}: {exc}"
                ) from exc

    return events