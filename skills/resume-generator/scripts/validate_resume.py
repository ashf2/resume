#!/usr/bin/env python3
"""Validate and normalize output/resume.json against JSON Schema and business rules."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ARRAY_FIELDS = (
    "educationList",
    "awardList",
    "workExpList",
    "skillList",
    "projectList",
    "workList",
)

TIME_ARRAY_FIELDS = {
    "educationList": "edu_time",
    "workExpList": "work_time",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def schema_path() -> Path:
    return Path(__file__).resolve().parent.parent / "schemas" / "resume.schema.json"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def parse_time_string(text: str) -> list[Any]:
    text = text.strip()
    if not text:
        return []
    parts = re.split(r"\s*[-–—~至]\s*", text)
    if len(parts) >= 2:
        end = parts[1].strip()
        if end in ("至今", "现在", "present", "Present"):
            end = None
        return [parts[0].strip(), end]
    return [text]


def ensure_array(value: Any, field_name: str) -> tuple[list, list[str]]:
    notes: list[str] = []
    if value is None:
        return [], notes
    if isinstance(value, list):
        return value, notes
    if isinstance(value, str):
        notes.append(f"{field_name} 原为字符串，已自动转为数组（请核对内容是否完整）")
        return [value], notes
    if isinstance(value, dict):
        notes.append(f"{field_name} 原为单个对象，已自动包装为数组")
        return [value], notes
    notes.append(f"{field_name} 类型异常（{type(value).__name__}），已重置为空数组")
    return [], notes


def normalize_time_field(item: dict, field: str) -> list[str]:
    notes: list[str] = []
    raw = item.get(field)
    if isinstance(raw, str) and raw.strip():
        item[field] = parse_time_string(raw)
        notes.append(f"已将 {field} 从字符串解析为时间数组")
    elif isinstance(raw, list):
        item[field] = raw
    elif raw is None:
        item[field] = []
    else:
        item[field] = [str(raw)]
        notes.append(f"{field} 类型异常，已转为数组")
    return notes


def normalize_resume_data(data: dict) -> tuple[dict, list[str]]:
    notes: list[str] = []
    result = json.loads(json.dumps(data))

    for field in ARRAY_FIELDS:
        fixed, field_notes = ensure_array(result.get(field), field)
        result[field] = fixed
        notes.extend(field_notes)

    for list_field, time_field in TIME_ARRAY_FIELDS.items():
        for item in result.get(list_field, []):
            if isinstance(item, dict):
                notes.extend(normalize_time_field(item, time_field))

    if isinstance(result.get("skillList"), list):
        result["skillList"] = [
            s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
            for s in result["skillList"]
        ]

    profile = result.setdefault("profile", {})
    for key in ("name", "email", "mobile", "github", "zhihu", "workExpYear", "position"):
        profile.setdefault(key, "")

    avatar = result.setdefault("avatar", {})
    avatar.setdefault("src", "")
    avatar.setdefault("hidden", True)

    aboutme = result.setdefault("aboutme", {})
    aboutme.setdefault("aboutme_desc", "")

    theme = result.setdefault("theme", {})
    theme.setdefault("id", "default")

    return result, notes


def validate_with_jsonschema(data: dict) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return []

    schema = load_json(schema_path())
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.path) or "根对象"
        errors.append(f"Schema：{path} — {err.message}")
    return errors


def validate_business_rules(data: dict) -> list[str]:
    errors: list[str] = []
    profile = data.get("profile") or {}

    if is_empty(profile.get("name")):
        errors.append("必填：姓名（profile.name）")

    if is_empty(profile.get("mobile")) and is_empty(profile.get("email")):
        errors.append("必填：联系方式 — 至少填写手机号（profile.mobile）或邮箱（profile.email）")

    if is_empty(profile.get("position")):
        errors.append("必填：意向职位（profile.position）")

    education = data.get("educationList") or []
    if not education:
        errors.append("必填：至少一条教育背景（educationList）")
    else:
        for i, edu in enumerate(education):
            prefix = f"教育经历[{i + 1}]"
            if not isinstance(edu, dict):
                errors.append(f"{prefix}：应为对象")
                continue
            if is_empty(edu.get("school")):
                errors.append(f"{prefix}：缺少学校（school）")
            if is_empty(edu.get("academic_degree")):
                errors.append(f"{prefix}：缺少学历（academic_degree）")
            edu_time = edu.get("edu_time")
            if not isinstance(edu_time, list) or not edu_time or is_empty(edu_time[0]):
                errors.append(f"{prefix}：缺少就读时间（edu_time，应为数组如 [\"2022.09\", \"2026.07\"]）")

    work = data.get("workExpList") or []
    projects = data.get("projectList") or []
    if not work and not projects:
        errors.append("必填：至少一条工作经历（workExpList）或项目经验（projectList）")

    for field in ARRAY_FIELDS:
        value = data.get(field)
        if value is not None and not isinstance(value, list):
            errors.append(f"格式错误：{field} 必须是数组，当前为 {type(value).__name__}")

    for i, work in enumerate(work):
        if not isinstance(work, dict):
            errors.append(f"工作经历[{i + 1}]：应为对象")
            continue
        wt = work.get("work_time")
        if not isinstance(wt, list) or not wt or is_empty(wt[0]):
            errors.append(f"工作经历[{i + 1}]：缺少工作时间（work_time，应为数组）")

    for i, proj in enumerate(projects):
        if not isinstance(proj, dict):
            errors.append(f"项目经验[{i + 1}]：应为对象")
            continue
        if is_empty(proj.get("project_name")):
            errors.append(f"项目经验[{i + 1}]：缺少项目名称（project_name）")

    theme = data.get("theme") or {}
    theme_id = theme.get("id", "default")
    if theme_id not in ("default", "blue-minimal", "classic"):
        errors.append(f"主题 id 无效：{theme_id}（应为 default / blue-minimal / classic）")

    return errors


def validate_resume_data(data: dict, use_schema: bool = True) -> tuple[list[str], list[str]]:
    schema_errors = validate_with_jsonschema(data) if use_schema else []
    business_errors = validate_business_rules(data)
    # Deduplicate while preserving order
    seen = set()
    merged: list[str] = []
    for err in schema_errors + business_errors:
        if err not in seen:
            seen.add(err)
            merged.append(err)
    return merged, schema_errors


def format_user_prompt(errors: list[str]) -> str:
    if not errors:
        return ""
    lines = ["您的输入中以下核心信息缺失或格式有误，请补充后我再为您生成排版：", ""]
    for err in errors:
        lines.append(f"- {err}")
    lines.append("")
    lines.append("请补充上述内容后告诉我，我会更新 resume.json 并继续生成简历。")
    return "\n".join(lines)


def validate_file(
    path: Path,
    normalize: bool = False,
    write_back: bool = False,
    use_schema: bool = True,
) -> tuple[bool, list[str], list[str]]:
    data = load_json(path)
    norm_notes: list[str] = []
    if normalize:
        data, norm_notes = normalize_resume_data(data)
        if write_back:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    errors, _ = validate_resume_data(data, use_schema=use_schema)
    return len(errors) == 0, errors, norm_notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate resume.json structure and required fields")
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=project_root() / "output" / "resume.json",
        help="Path to resume.json",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Auto-fix common format issues (string→array, time parsing) before validation",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write normalized JSON back to file (use with --normalize)",
    )
    parser.add_argument(
        "--no-schema",
        action="store_true",
        help="Skip JSON Schema validation (business rules only)",
    )
    parser.add_argument("--json", action="store_true", help="Output errors as JSON")
    args = parser.parse_args()

    input_path = args.input
    if not input_path.is_absolute():
        input_path = project_root() / input_path

    if not input_path.exists():
        print(f"文件不存在: {input_path}", file=sys.stderr)
        sys.exit(2)

    ok, errors, notes = validate_file(
        input_path,
        normalize=args.normalize,
        write_back=args.write,
        use_schema=not args.no_schema,
    )

    if args.json:
        print(json.dumps({"ok": ok, "errors": errors, "normalize_notes": notes}, ensure_ascii=False, indent=2))
    else:
        if notes:
            print("自动修正：")
            for n in notes:
                print(f"  - {n}")
            print()
        if ok:
            print("校验通过")
        else:
            print(format_user_prompt(errors))

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
