#!/usr/bin/env python3
"""Run content optimization checks: STAR analysis + optional JD match report."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_DRAFT = "output/resume.draft.json"
DEFAULT_JD = "output/job.jd.txt"
SCRIPTS = Path(__file__).resolve().parent


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else project_root() / path


def run_script(name: str, draft: Path, extra: list[str] = None) -> dict | list | None:
    cmd = [sys.executable, str(SCRIPTS / name), str(draft)]
    if extra:
        cmd.extend(extra)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0 and result.stderr:
        print(result.stderr, file=sys.stderr)
    if not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


def main() -> None:
    parser = argparse.ArgumentParser(description="Content optimization report (STAR + JD)")
    parser.add_argument("draft", type=Path, nargs="?", default=DEFAULT_DRAFT)
    parser.add_argument("--jd", type=Path, default=DEFAULT_JD)
    parser.add_argument(
        "--apply-jd",
        action="store_true",
        help="Apply JD skill reorder to draft (--write)",
    )
    parser.add_argument("-o", "--output", type=Path, help="Write combined JSON report")
    args = parser.parse_args()

    draft_path = resolve_path(args.draft)
    jd_path = resolve_path(args.jd)

    if not draft_path.exists():
        print(f"草稿不存在: {draft_path}", file=sys.stderr)
        sys.exit(2)

    report: dict = {"draft": str(draft_path), "star": None, "jd": None}

    star = run_script("analyze_star.py", draft_path, ["--json"])
    if star:
        report["star"] = star

    if jd_path.exists():
        if args.apply_jd:
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "jd_match.py"),
                    str(draft_path),
                    "--apply",
                    "--write",
                ],
                check=False,
            )
        jd_report = run_script("jd_match.py", draft_path, ["--json"])
        if jd_report:
            report["jd"] = jd_report
    else:
        report["jd_skipped"] = "未找到 job.jd.txt，跳过 JD 匹配"

    out_text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        out_path = resolve_path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text + "\n", encoding="utf-8")
        print(str(out_path))
    else:
        print(out_text)


if __name__ == "__main__":
    main()
