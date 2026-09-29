"""Offline research workflow example with an explicit human approval gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA_VERSION = 1
LATIN = re.compile(r"[a-z0-9]{2,}")
HAN = re.compile(r"[\u4e00-\u9fff]")
STOPWORDS = {"a", "an", "and", "are", "city", "example", "for", "in", "is", "of", "on", "the", "to", "what", "would"}


def _terms(text: str) -> set[str]:
    normalized = text.casefold()
    han = "".join(HAN.findall(normalized))
    return (set(LATIN.findall(normalized)) - STOPWORDS) | {han[i : i + 2] for i in range(len(han) - 1)}


def validate_corpus(payload: object) -> list[dict]:
    if not isinstance(payload, list) or not payload:
        raise ValueError("corpus must be a non-empty JSON array")
    seen = set()
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict) or set(item) != {"id", "title", "statement", "source_url"}:
            raise ValueError(f"fact {index} needs only id, title, statement and source_url")
        if any(not isinstance(item[key], str) or not item[key].strip() for key in item):
            raise ValueError(f"fact {index} has an empty field")
        parsed = urlsplit(item["source_url"])
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError(f"fact {index} needs a plain HTTPS source_url")
        if item["id"] in seen:
            raise ValueError(f"duplicate fact id: {item['id']}")
        seen.add(item["id"])
    return payload


def prepare(question: str, corpus: list[dict], limit: int = 3) -> dict:
    if not question.strip():
        raise ValueError("question cannot be empty")
    facts = validate_corpus(corpus)
    query = _terms(question)
    ranked = sorted(
        ((len(query & _terms(item["title"] + " " + item["statement"])), index, item) for index, item in enumerate(facts)),
        key=lambda row: (-row[0], row[1]),
    )
    selected = [item for score, _, item in ranked if score > 0][:limit]
    if not selected:
        raise ValueError("no matching facts; add evidence or rephrase the question")
    draft = {
        "title": question.strip(),
        "sections": [
            {"heading": "Evidence / 证据", "text": "\n".join(f"- {item['statement']} [source:{item['id']}]" for item in selected)},
            {"heading": "Open questions / 待核实", "text": "A reviewer must verify the cited facts and decide whether the draft is suitable for use. / 请复核引用和结论。"},
        ],
    }
    return {"schema_version": SCHEMA_VERSION, "stage": "needs_review", "question": question.strip(), "facts": selected, "draft": draft, "review": None}


def draft_digest(state: dict) -> str:
    material = {"question": state["question"], "facts": state["facts"], "draft": state["draft"]}
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def review(state: dict, decision: str, reviewer: str, comment: str = "") -> dict:
    if state.get("schema_version") != SCHEMA_VERSION or state.get("stage") not in {"needs_review", "rejected", "approved"}:
        raise ValueError("invalid or unsupported draft state")
    if decision not in {"approve", "reject"} or not reviewer.strip():
        raise ValueError("decision must be approve/reject and reviewer cannot be empty")
    if decision == "reject" and not comment.strip():
        raise ValueError("a rejection comment is required")
    state["stage"] = "approved" if decision == "approve" else "rejected"
    state["review"] = {
        "decision": decision,
        "reviewer": reviewer.strip(),
        "comment": comment.strip(),
        "draft_sha256": draft_digest(state),
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    return state


def export_markdown(state: dict) -> str:
    approval = state.get("review")
    if state.get("schema_version") != SCHEMA_VERSION or state.get("stage") != "approved" or not isinstance(approval, dict):
        raise ValueError("export blocked: human approval is required")
    if approval.get("decision") != "approve" or approval.get("draft_sha256") != draft_digest(state):
        raise ValueError("export blocked: draft changed after approval")
    facts = {item["id"]: item for item in state["facts"]}
    sections = state["draft"]["sections"]
    lines = [f"# {state['draft']['title']}", ""]
    for section in sections:
        lines.extend([f"## {section['heading']}", "", section["text"], ""])
    lines.extend(["## Sources / 来源", ""])
    for identifier, fact in facts.items():
        lines.append(f"- [source:{identifier}] {fact['title']} — {fact['source_url']}")
    lines.extend(["", f"Reviewed by / 复核人: {approval['reviewer']}", ""])
    return "\n".join(lines)


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline research draft with human review before export")
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("prepare")
    make.add_argument("--question", required=True)
    make.add_argument("--corpus", required=True, type=Path)
    make.add_argument("--out", required=True, type=Path)
    judge = sub.add_parser("review")
    judge.add_argument("state", type=Path)
    judge.add_argument("--decision", choices=("approve", "reject"), required=True)
    judge.add_argument("--reviewer", required=True)
    judge.add_argument("--comment", default="")
    send = sub.add_parser("export")
    send.add_argument("state", type=Path)
    send.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
            state = prepare(args.question, corpus)
            _write_json(args.out, state)
            print(f"Draft prepared: {args.out} (needs human review)")
        elif args.command == "review":
            state = json.loads(args.state.read_text(encoding="utf-8"))
            _write_json(args.state, review(state, args.decision, args.reviewer, args.comment))
            print(f"Review recorded: {args.decision}")
        else:
            state = json.loads(args.state.read_text(encoding="utf-8"))
            args.out.write_text(export_markdown(state), encoding="utf-8")
            print(f"Approved draft exported: {args.out}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
