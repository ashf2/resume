#!/usr/bin/env python3
"""Generate a Markdown summary preview from resume JSON (draft or final)."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_DRAFT = "output/resume.draft.json"
DEFAULT_FINAL = "output/resume.json"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def format_time_range(times: Any) -> str:
    if not isinstance(times, list) or not times:
        return ""
    start = times[0] if times[0] is not None else ""
    end = times[1] if len(times) > 1 else None
    if end is None:
        end_text = "至今"
    elif is_empty(end):
        end_text = "至今"
    else:
        end_text = str(end)
    if is_empty(start):
        return end_text if end_text != "至今" else ""
    return f"{start} – {end_text}"


def format_time_text(value: Any) -> str:
    if isinstance(value, list):
        return format_time_range(value)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return ""


def section_title(data: dict, key: str, default: str) -> str:
    return (data.get("titleNameMap") or {}).get(key) or default


def bullet_lines(text: str) -> list[str]:
    if is_empty(text):
        return []
    lines = [ln.strip() for ln in text.replace("\r\n", "\n").split("\n")]
    return [ln for ln in lines if ln]


def resume_to_markdown(data: dict, title: str = "简历内容摘要（待确认）") -> str:
    profile = data.get("profile") or {}
    lines: list[str] = [f"# {title}", ""]

    name = profile.get("name") or "（未填写姓名）"
    position = profile.get("position") or ""
    lines.append(f"## {name}")
    if position:
        lines.append(f"**意向职位**：{position}")
    lines.append("")

    contact_parts: list[str] = []
    if not is_empty(profile.get("mobile")):
        contact_parts.append(f"手机：{profile['mobile']}")
    if not is_empty(profile.get("email")):
        contact_parts.append(f"邮箱：{profile['email']}")
    if not is_empty(profile.get("github")):
        contact_parts.append(f"GitHub：{profile['github']}")
    if not is_empty(profile.get("zhihu")):
        contact_parts.append(f"知乎：{profile['zhihu']}")
    if not is_empty(profile.get("workExpYear")):
        contact_parts.append(f"工作年限：{profile['workExpYear']}")
    if contact_parts:
        lines.append("**联系方式**")
        for part in contact_parts:
            lines.append(f"- {part}")
        lines.append("")

    education = data.get("educationList") or []
    if education:
        lines.append(f"## {section_title(data, 'educationList', '教育背景')}")
        for i, edu in enumerate(education, 1):
            if not isinstance(edu, dict):
                continue
            school = edu.get("school") or "（学校未填）"
            degree = edu.get("academic_degree") or ""
            major = edu.get("major") or ""
            time_text = format_time_range(edu.get("edu_time"))
            meta = " · ".join(p for p in [degree, major, time_text] if p)
            lines.append(f"### {i}. {school}")
            if meta:
                lines.append(meta)
            lines.append("")

    skills = data.get("skillList") or []
    if skills:
        lines.append(f"## {section_title(data, 'skillList', '专业技能')}")
        for item in skills:
            if isinstance(item, str) and item.strip():
                lines.append(f"- {item.strip()}")
            elif isinstance(item, dict):
                text = item.get("skill_name") or item.get("name") or item.get("desc") or ""
                if str(text).strip():
                    lines.append(f"- {str(text).strip()}")
        lines.append("")

    work_list = data.get("workExpList") or []
    if work_list:
        lines.append(f"## {section_title(data, 'workExpList', '工作/实习经历')}")
        for i, work in enumerate(work_list, 1):
            if not isinstance(work, dict):
                continue
            company = work.get("company_name") or "（公司未填）"
            dept = work.get("department_name") or ""
            time_text = format_time_range(work.get("work_time"))
            header = f"### {i}. {company}"
            if dept:
                header += f" · {dept}"
            lines.append(header)
            if time_text:
                lines.append(f"*{time_text}*")
            for ln in bullet_lines(work.get("work_desc") or ""):
                lines.append(f"- {ln.lstrip('0123456789.、) ') if ln[0].isdigit() else ln}")
            lines.append("")

    projects = data.get("projectList") or []
    if projects:
        lines.append(f"## {section_title(data, 'projectList', '项目经验')}")
        for i, proj in enumerate(projects, 1):
            if not isinstance(proj, dict):
                continue
            name_p = proj.get("project_name") or "（项目未填）"
            role = proj.get("project_role") or ""
            time_text = format_time_text(proj.get("project_time"))
            header = f"### {i}. {name_p}"
            if role:
                header += f" · {role}"
            lines.append(header)
            if time_text:
                lines.append(f"*{time_text}*")
            if not is_empty(proj.get("project_desc")):
                lines.append(proj["project_desc"].strip())
            for ln in bullet_lines(proj.get("project_content") or ""):
                lines.append(f"- {ln.lstrip('0123456789.、) ') if ln and ln[0].isdigit() else ln}")
            lines.append("")

    about = (data.get("aboutme") or {}).get("aboutme_desc") or ""
    if not is_empty(about):
        lines.append(f"## {section_title(data, 'aboutme', '个人评价')}")
        lines.append(about.strip())
        lines.append("")

    theme = data.get("theme") or {}
    theme_id = theme.get("id") or "default"
    theme_name = theme.get("name") or theme_id
    lines.append("---")
    lines.append(
        "*以上为从您提供的信息中提取的内容摘要。您可通过对话修改任意段落；"
        "确认无误后回复「确认生成」以写入最终文件并渲染 HTML。*"
    )
    if theme_id != "default" or theme_name:
        lines.append(f"*当前主题偏好：{theme_name}（`{theme_id}`）*")

    return "\n".join(lines).rstrip() + "\n"


def resolve_input_path(path: Path | None, prefer_final: bool) -> Path:
    if path is not None:
        return path if path.is_absolute() else project_root() / path
    default_rel = DEFAULT_FINAL if prefer_final else DEFAULT_DRAFT
    return project_root() / default_rel


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Markdown preview from resume JSON")
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        help="Path to resume JSON (default: output/resume.draft.json or output/resume.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write preview to file (default: print to stdout)",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Read from output/resume.draft.json when input not specified",
    )
    parser.add_argument(
        "--final",
        action="store_true",
        help="Read from output/resume.json when input not specified",
    )
    parser.add_argument(
        "--title",
        default="简历内容摘要（待确认）",
        help="Markdown document title",
    )
    args = parser.parse_args()

    prefer_final = args.final and args.input is None
    input_path = resolve_input_path(args.input, prefer_final=prefer_final)

    if not input_path.exists():
        print(f"文件不存在: {input_path}", file=sys.stderr)
        print("请先由 Agent 写入中间态 output/resume.draft.json", file=sys.stderr)
        sys.exit(2)

    data = load_json(input_path)
    markdown = resume_to_markdown(data, title=args.title)

    if args.output:
        out_path = args.output if args.output.is_absolute() else project_root() / args.output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        print(str(out_path))
    else:
        print(markdown)


if __name__ == "__main__":
    main()
