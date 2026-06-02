# OSS Maintainer Workbench

OSS Maintainer Workbench is a small command line toolkit for open-source
maintainers who need a repeatable way to triage GitHub issues and pull requests.
It reads exported issue or PR metadata as JSON and produces a concise Markdown
digest with priority hints, likely labels, stale candidates, and release-note
items.

The project is intentionally dependency-light so maintainers can run it in CI,
cron jobs, or local release workflows without bringing in a large service.

## Features

- Classifies issues and pull requests by maintenance signal.
- Suggests labels such as `bug`, `security`, `docs`, `stale`, and `needs-info`.
- Highlights urgent items based on age, keywords, comments, and existing labels.
- Generates a Markdown report suitable for GitHub Actions job summaries.
- Includes a stable JSON input format for scripts and future API adapters.

## Install

```bash
python -m pip install .
```

For local development:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Usage

```bash
maintainer-workbench digest examples/issues.json
```

Example output:

```markdown
# Maintainer Digest

## High Priority

- #42 Fix token leak in debug logs
  Suggested labels: security, bug
```

## Input Format

The CLI accepts a JSON array of items:

```json
[
  {
    "number": 42,
    "title": "Fix token leak in debug logs",
    "body": "Debug output can expose API tokens.",
    "state": "open",
    "kind": "issue",
    "labels": ["bug"],
    "comments": 5,
    "created_at": "2026-05-01T12:00:00Z",
    "updated_at": "2026-05-29T12:00:00Z",
    "url": "https://github.com/example/project/issues/42"
  }
]
```

## Roadmap

- Add GitHub REST and GraphQL importers.
- Add maintainer-owned rulesets for custom labels and priority scoring.
- Add changelog grouping for merged pull requests.
- Add GitHub Actions examples for scheduled triage reports.

## License

MIT
