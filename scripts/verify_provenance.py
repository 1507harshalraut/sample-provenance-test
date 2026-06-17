#!/usr/bin/env python3
"""Verify AI provenance git note for a commit and emit a Markdown report.

Usage:
    python scripts/verify_provenance.py HEAD
    python scripts/verify_provenance.py e38be187 --output report.md
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def canonical_json(value: Any) -> str:
    if value is None:
        return "null"
    if not isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(v) for v in value) + "]"
    keys = sorted(value.keys())
    body = ",".join(
        json.dumps(k, ensure_ascii=False) + ":" + canonical_json(value[k]) for k in keys
    )
    return "{" + body + "}"


def verify_signature(manifest: dict[str, Any]) -> bool:
    signature = manifest.get("signature")
    public_key = manifest.get("publicKey")
    if not signature or not public_key:
        return False

    payload = {k: v for k, v in manifest.items() if k != "signature"}
    canonical = canonical_json(payload)

    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        key = serialization.load_pem_public_key(public_key.encode("utf-8"))
        if not isinstance(key, Ed25519PublicKey):
            return False
        key.verify(base64.b64decode(signature), canonical.encode("utf-8"))
        return True
    except Exception:
        return False


def read_note(repo: Path, commit: str) -> dict[str, Any] | None:
    try:
        raw = run_git(repo, "notes", "--ref=provenance", "show", commit)
        return json.loads(raw)
    except (RuntimeError, json.JSONDecodeError):
        return None


def resolve_commit(repo: Path, ref: str) -> str:
    return run_git(repo, "rev-parse", ref).strip()


def _tool_breakdown(manifest: dict[str, Any]) -> list[tuple[str, int]]:
    """Aggregate line counts by readable attribution label."""
    counts: dict[str, int] = {}

    for file_entry in manifest.get("files", []):
        for line in file_entry.get("lines", []):
            origin = line.get("origin", "unknown")
            tool = line.get("tool") or ""

            if origin == "human_typed":
                label = "Human typed"
            elif origin == "ai_generated":
                label = f"AI Generated ({tool or 'Unknown'})"
            elif origin == "ai_pasted":
                label = f"AI Pasted ({tool or 'browser LLM'})"
            elif origin == "pasted":
                label = "Human pasted (clipboard)"
            else:
                label = origin.replace("_", " ").title()

            counts[label] = counts.get(label, 0) + 1

    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))


def _interesting_lines(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Lines that are not plain human typed — for ChatGPT/Copilot visibility."""
    picked: list[dict[str, Any]] = []
    for file_entry in manifest.get("files", []):
        path = file_entry.get("path", "")
        for line in file_entry.get("lines", []):
            origin = line.get("origin", "")
            if origin in ("ai_generated", "ai_pasted", "pasted"):
                picked.append({**line, "file": path})
    return picked[:30]


def build_report(manifest: dict[str, Any], sig_ok: bool) -> str:
    commit = manifest.get("commit", "")[:12]
    author = manifest.get("author", {})
    key_id = manifest.get("keyId", "")
    sig_label = "valid" if sig_ok else "INVALID"
    sig_icon = "PASS" if sig_ok else "FAIL"

    lines_out = [
        "<!-- ai-provenance-report -->",
        "## AI Provenance Report",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Commit | `{commit}` |",
        f"| Author | {author.get('name', 'unknown')} |",
        f"| Signature | {sig_icon} **{sig_label}** |",
        f"| Key ID | `{key_id}` |",
        f"| Events captured | {manifest.get('eventCount', 0)} |",
        "",
    ]

    files = manifest.get("files", [])
    if not files:
        lines_out.append("_No files in manifest._")
        return "\n".join(lines_out)

    lines_out.append("### Per-file summary")
    lines_out.append("")
    lines_out.append("| File | Total lines | Human | AI generated | AI pasted | Pasted |")
    lines_out.append("|------|-------------|-------|--------------|-----------|--------|")

    for f in files:
        stats = f.get("stats", {})
        lines_out.append(
            f"| `{f.get('path', '')}` "
            f"| {stats.get('totalLines', 0)} "
            f"| {stats.get('human_typed', 0)} "
            f"| {stats.get('ai_generated', 0)} "
            f"| {stats.get('ai_pasted', 0)} "
            f"| {stats.get('pasted', 0)} |"
        )

    lines_out.extend(["", "### Attribution by tool", ""])
    lines_out.append("| Source | Lines |")
    lines_out.append("|--------|-------|")
    for label, count in _tool_breakdown(manifest):
        lines_out.append(f"| {label} | {count} |")

    ai_lines = _interesting_lines(manifest)
    if ai_lines:
        lines_out.extend(["", "### AI & paste lines (not just first 15)", ""])
        lines_out.append("| File | Line | Origin | Tool | Preview |")
        lines_out.append("|------|------|--------|------|---------|")
        for entry in ai_lines:
            preview = (entry.get("preview") or "").replace("|", "\\|").replace("\ufeff", "")[:50]
            lines_out.append(
                f"| `{entry.get('file', '')}` "
                f"| {entry.get('line', '')} "
                f"| {entry.get('origin', '')} "
                f"| {entry.get('tool', '') or '-'} "
                f"| `{preview}` |"
            )

    lines_out.extend(["", "### Sample line attributions (first 15 lines per file)", ""])
    for f in files:
        path = f.get("path", "")
        file_lines = f.get("lines", [])[:15]
        if not file_lines:
            continue
        lines_out.append(f"**`{path}`**")
        lines_out.append("")
        lines_out.append("| Line | Origin | Tool | Preview |")
        lines_out.append("|------|--------|------|---------|")
        for entry in file_lines:
            preview = (entry.get("preview") or "").replace("|", "\\|").replace("\ufeff", "")[:50]
            lines_out.append(
                f"| {entry.get('line', '')} "
                f"| {entry.get('origin', '')} "
                f"| {entry.get('tool', '') or '-'} "
                f"| `{preview}` |"
            )
        lines_out.append("")

    lines_out.append("---")
    lines_out.append("_Generated by AI Provenance GitHub Action_")
    return "\n".join(lines_out)


def build_failure_report(commit: str, reason: str) -> str:
    return "\n".join(
        [
            "<!-- ai-provenance-report -->",
            "## AI Provenance Report",
            "",
            f"FAIL **Check failed** for commit `{commit[:12]}`",
            "",
            reason,
            "",
            "### How to fix",
            "1. Install the **AI Provenance** VS Code extension",
            "2. Edit code with the plugin active (events → `~/.provenance/events.jsonl`)",
            "3. Run **AI Provenance: Install git post-commit hook**",
            "4. Commit again — hook attaches a signed note",
            "5. Push notes: `git push origin refs/notes/provenance`",
            "",
            "---",
            "_Generated by AI Provenance GitHub Action_",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify provenance git note")
    parser.add_argument("commit", help="Commit SHA or ref (e.g. HEAD)")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--output", "-o", help="Write Markdown report to file")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    try:
        commit = resolve_commit(repo, args.commit)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    manifest = read_note(repo, commit)
    if manifest is None:
        report = build_failure_report(
            commit,
            "No provenance git note found at `refs/notes/provenance` for this commit.",
        )
        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
        else:
            print(report)
        return 1

    sig_ok = verify_signature(manifest)
    report = build_report(manifest, sig_ok)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report)

    return 0 if sig_ok else 1


if __name__ == "__main__":
    sys.exit(main())
