#!/usr/bin/env python3
"""Inject resume.json into templates and write standalone HTML resume files."""

import argparse
import base64
import copy
import json
import mimetypes
import re
import sys
from pathlib import Path

THEME_IDS = ("default", "blue-minimal", "classic")


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def templates_dir() -> Path:
    return project_root() / "templates"


def load_theme_catalog() -> dict:
    catalog_path = templates_dir() / "themes.json"
    if not catalog_path.exists():
        return {}
    with catalog_path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {t["id"]: t for t in data.get("themes", [])}


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name.strip())
    return name or "简历"


def apply_theme_preset(data: dict, theme_id: str | None = None) -> dict:
    catalog = load_theme_catalog()
    result = copy.deepcopy(data)
    theme = result.get("theme") or {}

    selected_id = theme_id or theme.get("id") or "default"
    if selected_id not in catalog:
        selected_id = "default"

    preset = catalog[selected_id]
    theme["id"] = selected_id
    theme["name"] = preset.get("name", selected_id)
    for key in ("color", "tagColor", "pageBg", "cardBg", "textMain", "textLight", "lineColor"):
        if preset.get(key):
            theme[key] = preset[key]
    result["theme"] = theme
    return result


def resolve_template_path(data: dict, explicit: Path | None = None) -> Path:
    if explicit:
        return explicit
    catalog = load_theme_catalog()
    theme_id = (data.get("theme") or {}).get("id", "default")
    preset = catalog.get(theme_id, {})
    template_name = preset.get("template", "resume.html")
    path = templates_dir() / template_name
    if not path.exists():
        path = templates_dir() / "resume.html"
    return path


def resolve_avatar_for_render(data: dict, output_path: Path, embed_avatar: bool = False) -> dict:
    """Resolve local avatar paths relative to output/; optionally embed as data URL."""
    result = copy.deepcopy(data)
    avatar = result.get("avatar") or {}
    src = (avatar.get("src") or "").strip()
    if avatar.get("hidden") or not src:
        return result
    if src.startswith("data:") or is_url(src):
        return result

    root = project_root()
    candidates = [
        output_path.parent / src,
        output_dir() / src,
        root / src,
        root / "output" / src,
    ]
    image_path = next((p for p in candidates if p.exists()), None)
    if image_path is None:
        return result

    if embed_avatar:
        avatar["src"] = to_data_url(image_path)
    else:
        try:
            avatar["src"] = image_path.relative_to(output_path.parent).as_posix()
        except ValueError:
            avatar["src"] = f"avatars/{image_path.name}"

    result["avatar"] = avatar
    return result


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def output_dir() -> Path:
    return project_root() / "output"


def to_data_url(image_path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(image_path))
    mime = mime or "image/jpeg"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def render_resume(
    json_path: Path,
    output_path: Path,
    template_path: Path | None = None,
    theme_id: str | None = None,
    embed_avatar: bool = False,
) -> Path:
    root = project_root()
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    data = apply_theme_preset(data, theme_id)
    data = resolve_avatar_for_render(data, output_path, embed_avatar)
    template = template_path or resolve_template_path(data)
    if not template.is_absolute():
        template = root / template
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template}")

    html = template.read_text(encoding="utf-8")
    if "__RESUME_DATA__" not in html:
        raise ValueError("Template missing __RESUME_DATA__ placeholder")

    json_embed = json.dumps(data, ensure_ascii=False, indent=4)
    rendered = html.replace("__RESUME_DATA__", json_embed)

    profile = data.get("profile") or {}
    title = profile.get("name", "简历")
    if "<title>" in rendered:
        rendered = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", rendered, count=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def default_output_path(data: dict, theme_id: str | None = None, include_theme_in_name: bool = False) -> Path:
    profile = data.get("profile") or {}
    name = sanitize_filename(profile.get("name", "简历"))
    position = sanitize_filename(profile.get("position", ""))
    theme = apply_theme_preset(data, theme_id)
    tid = (theme.get("theme") or {}).get("id", "default")

    out_dir = project_root() / "output"
    parts = [name]
    if position:
        parts.append(position)
    if include_theme_in_name or tid != "default":
        parts.append(tid)
    return out_dir / f"{'-'.join(parts)}.html"


def list_themes_text() -> str:
    catalog = load_theme_catalog()
    lines = ["可选简历主题："]
    for tid in THEME_IDS:
        preset = catalog.get(tid, {})
        lines.append(f"  - {tid}: {preset.get('name', tid)} — {preset.get('description', '')}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render resume HTML from resume.json")
    parser.add_argument("input", type=Path, nargs="?", help="Path to resume.json")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output HTML path")
    parser.add_argument("-t", "--template", type=Path, default=None, help="HTML template path")
    parser.add_argument(
        "--theme",
        choices=THEME_IDS,
        help="Theme id: default, blue-minimal, classic",
    )
    parser.add_argument(
        "--all-themes",
        action="store_true",
        help="Generate HTML for all three themes",
    )
    parser.add_argument("--list-themes", action="store_true", help="List available themes")
    parser.add_argument(
        "--embed-avatar",
        action="store_true",
        help="Embed local avatar as base64 in HTML (portable single file)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip resume.json validation (not recommended)",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="After HTML render, export PDF via Playwright (export_pdf.py)",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Do not export PDF (overrides --pdf)",
    )
    args = parser.parse_args()

    if args.list_themes:
        print(list_themes_text())
        return

    if not args.input:
        parser.error("input resume.json is required unless --list-themes is used")

    input_path = args.input
    if not input_path.is_absolute():
        input_path = project_root() / input_path

    if not args.skip_validation:
        from validate_resume import format_user_prompt, validate_file

        ok, errors, _ = validate_file(input_path, normalize=False, write_back=False)
        if not ok:
            print(format_user_prompt(errors), file=sys.stderr)
            sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    outputs: list[Path] = []

    if args.all_themes:
        for tid in THEME_IDS:
            themed = apply_theme_preset(data, tid)
            out_path = default_output_path(themed, tid, include_theme_in_name=True)
            outputs.append(render_resume(input_path, out_path, args.template, tid, args.embed_avatar))
    else:
        themed = apply_theme_preset(data, args.theme)
        out_path = args.output or default_output_path(themed, args.theme)
        outputs.append(render_resume(input_path, out_path, args.template, args.theme, args.embed_avatar))

    for path in outputs:
        print(str(path))

    if args.pdf and not args.no_pdf:
        from export_pdf import export_pdfs_from_paths

        pdfs = export_pdfs_from_paths(outputs, margin_mm=0)
        for p in pdfs:
            print(str(p))


if __name__ == "__main__":
    main()
