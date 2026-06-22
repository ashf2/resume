#!/usr/bin/env python3
"""Copy or download avatar image, update resume.json for HTML resume display."""

import argparse
import base64
import json
import mimetypes
import re
import shutil
import urllib.request
from pathlib import Path

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name.strip())
    return name or "avatar"


def output_dir() -> Path:
    return project_root() / "output"


def avatars_dir() -> Path:
    path = output_dir() / "avatars"
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def download_image(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    return dest


def resolve_source(source: str) -> Path:
    path = Path(source).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {source}")
    return path


def pick_extension(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in ALLOWED_EXT:
        return ext
    return ".jpg"


def to_data_url(image_path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(image_path))
    mime = mime or "image/jpeg"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def update_resume_json(resume_path: Path, avatar_src: str, hidden: bool = False) -> None:
    with resume_path.open(encoding="utf-8") as f:
        data = json.load(f)
    data["avatar"] = {"src": avatar_src, "hidden": hidden}
    resume_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def setup_from_file(
    source: Path,
    resume_path: Path,
    basename: str | None = None,
    embed: bool = False,
) -> str:
    ext = pick_extension(source)
    name = sanitize_filename(basename or source.stem)
    dest = avatars_dir() / f"{name}{ext}"
    shutil.copy2(source, dest)

    if embed:
        src = to_data_url(dest)
    else:
        src = f"avatars/{dest.name}"

    update_resume_json(resume_path, src, hidden=False)
    return src


def setup_from_url(url: str, resume_path: Path, basename: str | None = None, embed: bool = False) -> str:
    name = sanitize_filename(basename or "avatar")
    dest = avatars_dir() / f"{name}.jpg"
    download_image(url, dest)

    if embed:
        src = to_data_url(dest)
    else:
        src = f"avatars/{dest.name}"

    update_resume_json(resume_path, src, hidden=False)
    return src


def hide_avatar(resume_path: Path) -> None:
    with resume_path.open(encoding="utf-8") as f:
        data = json.load(f)
    avatar = data.get("avatar") or {}
    avatar["hidden"] = True
    if not avatar.get("src"):
        avatar["src"] = ""
    data["avatar"] = avatar
    resume_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup resume avatar image")
    parser.add_argument("source", nargs="?", help="Local image path or http(s) URL")
    parser.add_argument(
        "-r",
        "--resume",
        type=Path,
        default=output_dir() / "resume.json",
        help="Path to resume.json (default: output/resume.json)",
    )
    parser.add_argument("-n", "--name", help="Avatar file basename (default: from profile.name or source)")
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Store base64 data URL in resume.json (single-file portable HTML)",
    )
    parser.add_argument("--hide", action="store_true", help="Hide avatar in resume")
    args = parser.parse_args()

    resume_path = args.resume
    if not resume_path.is_absolute():
        resume_path = project_root() / resume_path

    if args.hide:
        hide_avatar(resume_path)
        print("avatar hidden")
        return

    if not args.source:
        parser.error("source image path or URL is required unless --hide is used")

    basename = args.name
    if not basename and resume_path.exists():
        with resume_path.open(encoding="utf-8") as f:
            data = json.load(f)
        basename = (data.get("profile") or {}).get("name")

    if is_url(args.source):
        src = setup_from_url(args.source, resume_path, basename, args.embed)
    else:
        src = setup_from_file(resolve_source(args.source), resume_path, basename, args.embed)

    print(src)


if __name__ == "__main__":
    main()
