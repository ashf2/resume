#!/usr/bin/env python3
"""Detect thin work/project descriptions and suggest STAR-style expansion."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_DRAFT = "output/resume.draft.json"

METRIC_PATTERN = re.compile(
    r"(\d+%|\d+\s*倍|\d+[kK]|"
    r"\d+\s*万|\d+\s*ms|\d+\s*s|"
    r"提升|降低|增长|减少|优化了?\d+|"
    r"\d+\s*人|\d+\s*个|QPS|TPS|DAU)",
    re.IGNORECASE,
)

STAR_MARKERS = re.compile(
    r"(情境|任务|行动|结果|背景|负责|实现|完成|主导|参与|"
    r"situation|task|action|result|achieved|improved)",
    re.IGNORECASE,
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else project_root() / path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bullet_lines(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    lines = [ln.strip() for ln in text.replace("\r\n", "\n").split("\n")]
    result = []
    for ln in lines:
        if not ln:
            continue
        cleaned = re.sub(r"^[\d]+[.、)\]]\s*", "", ln)
        if cleaned:
            result.append(cleaned)
    return result


def thinness_score(text: str, min_chars: int, min_bullets: int) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0
    stripped = text.strip()
    bullets = bullet_lines(stripped)

    if len(stripped) < min_chars:
        score += 2
        reasons.append(f"总字数不足（{len(stripped)} < {min_chars}）")

    if len(bullets) < min_bullets:
        score += 2
        reasons.append(f"要点过少（{len(bullets)} < {min_bullets} 条）")

    if bullets and all(len(b) < 25 for b in bullets):
        score += 1
        reasons.append("各条描述过于简短（<25 字）")

    if not METRIC_PATTERN.search(stripped):
        score += 2
        reasons.append("缺少可量化指标（百分比、倍数、耗时、规模等）")

    if not STAR_MARKERS.search(stripped):
        score += 1
        reasons.append("缺少 STAR 结构信号（情境/任务/行动/结果）")

    return score, reasons


def star_prompt_template(entry_type: str, title: str, original: str) -> str:
    return (
        f"请将以下「{entry_type}：{title}」的描述扩写为 2–4 条简历要点，"
        f"隐含 STAR 结构（情境→任务→行动→结果），并尽量补充合理的数据指标。\n"
        f"**约束**：不得编造用户未提及的技术栈或成果；无数据时可写定性收益。\n"
        f"**原文**：\n{original.strip()}\n"
        f"**输出格式**：每条一行，无需标注 S/T/A/R 字母。"
    )


def analyze_work_items(items: list[dict], threshold: int) -> list[dict]:
    findings = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        desc = item.get("work_desc") or ""
        score, reasons = thinness_score(desc, min_chars=80, min_bullets=2)
        if score >= threshold:
            company = item.get("company_name") or f"工作经历[{i + 1}]"
            dept = item.get("department_name") or ""
            title = f"{company} · {dept}".strip(" ·")
            findings.append(
                {
                    "path": f"workExpList[{i}].work_desc",
                    "type": "work",
                    "index": i,
                    "title": title,
                    "thinness_score": score,
                    "reasons": reasons,
                    "original": desc.strip(),
                    "star_prompt": star_prompt_template("工作/实习经历", title, desc),
                }
            )
    return findings


def analyze_project_items(items: list[dict], threshold: int) -> list[dict]:
    findings = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        content = item.get("project_content") or ""
        desc = item.get("project_desc") or ""
        combined = f"{desc}\n{content}".strip()
        score, reasons = thinness_score(combined, min_chars=100, min_bullets=2)
        if score >= threshold:
            name = item.get("project_name") or f"项目[{i + 1}]"
            role = item.get("project_role") or ""
            title = f"{name} · {role}".strip(" ·")
            findings.append(
                {
                    "path": f"projectList[{i}].project_content",
                    "type": "project",
                    "index": i,
                    "title": title,
                    "thinness_score": score,
                    "reasons": reasons,
                    "original": combined,
                    "star_prompt": star_prompt_template("项目经验", title, combined),
                    "also_update": f"projectList[{i}].project_desc",
                }
            )
    return findings


def format_markdown_report(findings: list[dict]) -> str:
    if not findings:
        return "未发现需要 STAR 扩写的单薄描述。\n"
    lines = ["# STAR 扩写建议", "", f"共 {len(findings)} 处描述建议由 Agent 按 STAR 原则润色：", ""]
    for f in findings:
        lines.append(f"## {f['title']}")
        lines.append(f"- JSON 路径：`{f['path']}`")
        lines.append(f"- 单薄度评分：{f['thinness_score']}")
        for r in f["reasons"]:
            lines.append(f"  - {r}")
        lines.append("")
        lines.append("**原文摘要**：")
        lines.append(f"> {f['original'][:200]}{'…' if len(f['original']) > 200 else ''}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze thin descriptions for STAR expansion")
    parser.add_argument("draft", type=Path, nargs="?", default=DEFAULT_DRAFT)
    parser.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="Thinness score threshold to flag (default: 3)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("-o", "--output", type=Path, help="Write markdown report to file")
    args = parser.parse_args()

    draft_path = resolve_path(args.draft)
    if not draft_path.exists():
        print(f"草稿不存在: {draft_path}", file=sys.stderr)
        sys.exit(2)

    data = load_json(draft_path)
    findings = analyze_work_items(data.get("workExpList") or [], args.threshold)
    findings.extend(analyze_project_items(data.get("projectList") or [], args.threshold))
    findings.sort(key=lambda x: -x["thinness_score"])

    report: dict[str, Any] = {
        "draft": str(draft_path),
        "threshold": args.threshold,
        "count": len(findings),
        "findings": findings,
        "agent_instruction": (
            "对 findings 中每一项，使用 star_prompt 调用大模型扩写，"
            "将结果写入对应 path；project 类型可拆分 project_desc 与 project_content。"
            "禁止编造未在原文出现的技术或数字。"
        ),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.output:
        out = resolve_path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(format_markdown_report(findings), encoding="utf-8")
        print(str(out))
    else:
        print(format_markdown_report(findings))

    sys.exit(0)


if __name__ == "__main__":
    main()
