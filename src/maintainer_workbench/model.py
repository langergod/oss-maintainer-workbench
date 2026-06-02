from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class WorkItem:
    number: int
    title: str
    body: str = ""
    state: str = "open"
    kind: str = "issue"
    labels: tuple[str, ...] = field(default_factory=tuple)
    comments: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    url: str | None = None

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "WorkItem":
        return cls(
            number=int(payload["number"]),
            title=str(payload.get("title", "")).strip(),
            body=str(payload.get("body", "") or ""),
            state=str(payload.get("state", "open")),
            kind=str(payload.get("kind", "issue")),
            labels=tuple(str(label).lower() for label in payload.get("labels", [])),
            comments=int(payload.get("comments", 0)),
            created_at=parse_timestamp(payload.get("created_at")),
            updated_at=parse_timestamp(payload.get("updated_at")),
            url=payload.get("url"),
        )
