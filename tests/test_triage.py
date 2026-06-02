from datetime import datetime, timezone

from maintainer_workbench.model import WorkItem
from maintainer_workbench.triage import classify_item, render_digest


NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def test_security_issue_is_high_priority() -> None:
    item = WorkItem(
        number=42,
        title="Fix token leak in debug logs",
        body="Debug mode can expose a secret token.",
        labels=("bug",),
        comments=5,
    )

    result = classify_item(item, now=NOW)

    assert result.priority == "high"
    assert "security" in result.suggested_labels
    assert "bug" in result.suggested_labels


def test_stale_needs_info_issue_is_low_priority() -> None:
    item = WorkItem(
        number=7,
        title="Cannot reproduce setup error",
        body="The report is unclear and missing reproduction details.",
        state="open",
        updated_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
    )

    result = classify_item(item, now=NOW)

    assert result.priority == "low"
    assert "needs-info" in result.suggested_labels
    assert "stale" in result.suggested_labels


def test_digest_groups_results() -> None:
    items = [
        WorkItem(number=1, title="Security regression", body="credential leak"),
        WorkItem(number=2, title="Update README typo"),
    ]
    digest = render_digest([classify_item(item, now=NOW) for item in items])

    assert "# Maintainer Digest" in digest
    assert "## High Priority" in digest
    assert "#1 Security regression" in digest
    assert "## Low Priority" in digest
