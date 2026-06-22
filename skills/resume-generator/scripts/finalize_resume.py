#!/usr/bin/env python3
"""Promote validated draft resume JSON to final output/resume.json after HITL confirm."""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_DRAFT = "output/resume.draft.json"
DEFAULT_FINAL = "output/resume.json"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else project_root() / path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy validated resume.draft.json to resume.json after user confirmation"
    )
    parser.add_argument(
        "--draft",
        type=Path,
        default=DEFAULT_DRAFT,
        help="Draft JSON path (default: output/resume.draft.json)",
    )
    parser.add_argument(
        "--final",
        type=Path,
        default=DEFAULT_FINAL,
        help="Final JSON path (default: output/resume.json)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation before promoting (not recommended)",
    )
    args = parser.parse_args()

    draft_path = resolve_path(args.draft)
    final_path = resolve_path(args.final)

    if not draft_path.exists():
        print(f"草稿不存在: {draft_path}", file=sys.stderr)
        print("请先完成信息提取并写入 output/resume.draft.json", file=sys.stderr)
        sys.exit(2)

    if not args.skip_validation:
        from validate_resume import format_user_prompt, validate_file

        ok, errors, _ = validate_file(draft_path, normalize=False, write_back=False)
        if not ok:
            print(format_user_prompt(errors), file=sys.stderr)
            sys.exit(1)

    data = json.loads(draft_path.read_text(encoding="utf-8"))
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(final_path))


if __name__ == "__main__":
    main()
