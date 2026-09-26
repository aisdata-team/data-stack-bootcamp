#!/usr/bin/env python3
"""List the units and questions whose source files have changed since they were written.

Every unit and item pins its sources as {repo, path, commit}. For each distinct
source this compares the file's blob SHA at the pinned commit with its blob SHA on
`main`, and classifies it:

    unchanged   same blob — nothing to review
    changed     the file moved on — review the units/items that cite it
    missing     the file is gone from main — rewrite what cites it
    unreadable  the read failed (bad pin, API error) — the check did NOT run for it

It FAILS CLOSED. No token, an unreadable source, or no sources at all is never
reported as clean: a drift check that says "clean" because it could not look is
worse than no check.

Exit codes: 0 clean · 1 drift found (changed/missing) · 2 not run or incomplete.

    BOOTCAMP_SOURCES_TOKEN=… python3 scripts/check_source_drift.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from bank import CONTENT_DIR, ContentError, load_questions, load_units

OWNER = "aisdata-team"
API = "https://api.github.com"
TOKEN_ENV = "BOOTCAMP_SOURCES_TOKEN"
ORDER = ("unreadable", "missing", "changed", "unchanged")


class FetchError(Exception):
    pass


def fetch_blob_sha(repo: str, path: str, ref: str, token: str) -> str | None:
    """Blob SHA of `path` at `ref`, None if the file does not exist there. Raises FetchError otherwise.

    The only network call in this module — tests monkeypatch it.
    """
    url = f"{API}/repos/{OWNER}/{repo}/contents/{urllib.parse.quote(path)}?ref={urllib.parse.quote(ref)}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise FetchError(f"HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise FetchError(str(e)) from e
    if not isinstance(body, dict) or body.get("type") != "file" or not body.get("sha"):
        raise FetchError("not a file")
    return body["sha"]


def collect_sources(content_dir: Path) -> dict[tuple[str, str, str], list[str]]:
    """{(repo, path, commit): [who cites it, …]} across units and question items."""
    cited: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    def add(sources, who: str) -> None:
        for src in sources or []:
            if isinstance(src, dict):
                cited[(str(src.get("repo")), str(src.get("path")), str(src.get("commit")))].append(who)

    for unit in load_units(content_dir):
        add(unit.meta.get("sources"), f"unit {unit.id or unit.folder.name}")
    for qf in load_questions(content_dir):
        for item in qf.items:
            if isinstance(item, dict):
                add(item.get("sources"), f"item {item.get('id')}")
    return dict(cited)


def classify(key: tuple[str, str, str], token: str) -> tuple[str, str]:
    repo, path, commit = key
    try:
        pinned = fetch_blob_sha(repo, path, commit, token)
        if pinned is None:
            return "unreadable", f"not found at the pinned commit {commit[:12]} — the pin is wrong"
        current = fetch_blob_sha(repo, path, "main", token)
    except FetchError as e:
        return "unreadable", str(e)
    if current is None:
        return "missing", "gone from main"
    return ("unchanged", "") if current == pinned else ("changed", f"changed since {commit[:12]}")


def run(content_dir: Path, token: str | None) -> tuple[int, str]:
    if not token:
        return (
            2,
            f"## Source drift — NOT RUN\n\n`{TOKEN_ENV}` is not set, so no source was read. "
            "This is not a clean result.",
        )
    try:
        cited = collect_sources(content_dir)
    except ContentError as e:
        return 2, f"## Source drift — NOT RUN\n\nCould not load content: {e}"
    if not cited:
        return 2, "## Source drift — NOT RUN\n\nNo sources found in the content. An empty check is not a clean one."

    results = {key: classify(key, token) for key in cited}
    counts = {state: sum(1 for s, _ in results.values() if s == state) for state in ORDER}
    lines = [
        "## Source drift",
        "",
        " · ".join(f"{counts[s]} {s}" for s in ORDER),
        "",
    ]
    for state in ORDER[:-1]:
        keys = sorted(k for k, (s, _) in results.items() if s == state)
        if not keys:
            continue
        lines.append(f"### {state}")
        for key in keys:
            repo, path, _commit = key
            lines.append(f"- `{repo}/{path}` — {results[key][1]}; cited by {', '.join(sorted(cited[key]))}")
        lines.append("")
    if counts["unreadable"]:
        lines.append("**Incomplete:** some sources could not be read, so this is not a clean result.")
        return 2, "\n".join(lines)
    if counts["changed"] or counts["missing"]:
        return 1, "\n".join(lines)
    lines.append("All sources unchanged.")
    return 0, "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="List content whose source files have changed.")
    parser.add_argument("--content", type=Path, default=CONTENT_DIR)
    args = parser.parse_args(argv)
    code, report = run(args.content, os.environ.get(TOKEN_ENV))
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
