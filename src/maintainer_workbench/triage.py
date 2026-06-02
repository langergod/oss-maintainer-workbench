from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .model import WorkItem


SECURITY_TERMS = {"cve", "credential", "exploit", "leak", "secret", "security", "token"}
BUG_TERMS = {"bug", "crash", "error", "exception", "fail", "regression", "traceback"}
DOC_TERMS = {"docs", "documentation", "readme", "typo"}
NEEDS_INFO_TERMS = {"cannot reproduce", "unclear", "missing reproduction", "needs info"}


@dataclass(frozen=True)
class TriageResult:
    item: WorkItem
    score: int
    priority: str
    suggested_labels: tuple[str, ...]
    reasons: tuple[str, ...]


def classify_item(item: WorkItem, now: datetime | None = None) -> TriageResult:
    now = now or datetime.now(timezone.utc)
    text = f"{item.title}\n{item.body}".lower()
    labels = set(item.labels)
    suggested: set[str] = set()
    reasons: list[str] = []
    score = 0

    if _contains_any(text, SECURITY_TERMS) or "security" in labels:
        suggested.update({"security", "bug"})
        reasons.append("security-sensitive wording or label")
        score += 80

    if _contains_any(text, BUG_TERMS) or "bug" in labels:
        suggested.add("bug")
        reasons.append("bug or regression signal")
        score += 30

    if _contains_any(text, DOC_TERMS) or "documentation" in labels:
        suggested.add("docs")
        reasons.append("documentation-focused change")
        score += 5

    if _contains_any(text, NEEDS_INFO_TERMS) or "needs-info" in labels:
        suggested.add("needs-info")
        reasons.append("requires clearer reproduction details")
        score -= 10

    if item.comments >= 8:
        reasons.append("high discussion volume")
        score += 20
    elif item.comments >= 3:
        reasons.append("moderate discussion volume")
        score += 10

    if item.updated_at and (now - item.updated_at).days >= 45 and item.state == "open":
        suggested.add("stale")
        reasons.append("open without recent activity")
        score -= 15

    priority = _priority(score)
    if not suggested:
        suggested.add("triage")
    if not reasons:
        reasons.append("no strong signal detected")

    return TriageResult(
        item=item,
        score=score,
        priority=priority,
        suggested_labels=tuple(sorted(suggested)),
        reasons=tuple(reasons),
    )


def render_digest(results: list[TriageResult]) -> str:
    groups = {
        "high": [result for result in results if result.priority == "high"],
        "medium": [result for result in results if result.priority == "medium"],
        "low": [result for result in results if result.priority == "low"],
    }
    lines = ["# Maintainer Digest", ""]
    for priority, title in (("high", "High Priority"), ("medium", "Medium Priority"), ("low", "Low Priority")):
        lines.extend([f"## {title}", ""])
        if not groups[priority]:
            lines.extend(["No items.", ""])
            continue
        for result in sorted(groups[priority], key=lambda entry: entry.score, reverse=True):
            link = f" [{result.item.url}]({result.item.url})" if result.item.url else ""
            labels = ", ".join(result.suggested_labels)
            reasons = "; ".join(result.reasons)
            lines.extend(
                [
                    f"- #{result.item.number} {result.item.title}{link}",
                    f"  Suggested labels: {labels}",
                    f"  Reasons: {reasons}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _priority(score: int) -> str:
    if score >= 60:
        return "high"
    if score >= 15:
        return "medium"
    return "low"
