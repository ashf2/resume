#!/usr/bin/env python3
"""Save target job description (JD) for JD-matching optimization."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_JD = "output/job.jd.txt"
DEFAULT_CONTEXT = "output/job.context.json"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"


def load_keyword_data() -> dict:
    path = data_dir() / "jd_keywords.json"
    if not path.exists():
        return {"clusters": {}, "tech_terms": []}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def tokenize_jd(text: str) -> list[str]:
    lowered = text.lower()
    tokens: list[str] = []
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", lowered):
        if len(word) >= 2:
            tokens.append(word)
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        tokens.append(chunk)
    return tokens


def extract_keywords(text: str) -> list[str]:
    keyword_data = load_keyword_data()
    lowered = text.lower()
    found: list[str] = []
    seen: set[str] = set()

    for term in keyword_data.get("tech_terms", []):
        key = term.lower()
        if key in seen:
            continue
        if key in lowered or term in text:
            seen.add(key)
            found.append(term)

    for token in tokenize_jd(text):
        key = token.lower()
        if key not in seen and len(key) >= 2:
            seen.add(key)
            found.append(token)

    return found[:80]


def detect_dominant_clusters(text: str, keyword_data: dict) -> list[dict]:
    lowered = text.lower()
    scores: list[tuple[str, int, list[str]]] = []
    for cluster_id, terms in keyword_data.get("clusters", {}).items():
        matched = []
        score = 0
        for term in terms:
            t_lower = term.lower()
            if t_lower in lowered or term in text:
                matched.append(term)
                score += 1
        if score:
            scores.append((cluster_id, score, matched))
    scores.sort(key=lambda x: -x[1])
    return [
        {"cluster": cid, "score": score, "matched_terms": matched[:12]}
        for cid, score, matched in scores[:5]
    ]


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else project_root() / path


def main() -> None:
    parser = argparse.ArgumentParser(description="Save job description for resume optimization")
    parser.add_argument("text", nargs="?", help="JD text (or use -f / --stdin)")
    parser.add_argument("-f", "--file", type=Path, help="Read JD from file")
    parser.add_argument("--stdin", action="store_true", help="Read JD from stdin")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_JD, help="JD text output path")
    parser.add_argument(
        "--context",
        type=Path,
        default=DEFAULT_CONTEXT,
        help="Structured context JSON path",
    )
    parser.add_argument("--title", help="Target job title (optional)")
    parser.add_argument("--json", action="store_true", help="Print context JSON to stdout")
    args = parser.parse_args()

    if args.stdin:
        raw = sys.stdin.read()
    elif args.file:
        file_path = resolve_path(args.file)
        raw = file_path.read_text(encoding="utf-8")
    elif args.text:
        raw = args.text
    else:
        parser.error("Provide JD via argument, -f, or --stdin")

    text = normalize_text(raw)
    if not text:
        print("JD 内容为空", file=sys.stderr)
        sys.exit(1)

    keyword_data = load_keyword_data()
    keywords = extract_keywords(text)
    clusters = detect_dominant_clusters(text, keyword_data)

    out_jd = resolve_path(args.output)
    out_ctx = resolve_path(args.context)
    out_jd.parent.mkdir(parents=True, exist_ok=True)
    out_jd.write_text(text + "\n", encoding="utf-8")

    context = {
        "title": args.title or "",
        "jd_path": str(out_jd.relative_to(project_root())).replace("\\", "/"),
        "keywords": keywords,
        "dominant_clusters": clusters,
        "char_count": len(text),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    out_ctx.write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print(f"JD 已保存: {out_jd}")
        print(f"上下文: {out_ctx}")
        if clusters:
            top = clusters[0]
            print(f"主导方向: {top['cluster']} (匹配 {top['score']} 项)")


if __name__ == "__main__":
    main()
