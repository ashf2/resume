#!/usr/bin/env python3
"""Export resume HTML to PDF using Playwright headless Chromium."""

import argparse
import sys
from pathlib import Path

DEFAULT_MARGIN_MM = 0


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else project_root() / path


def default_pdf_path(html_path: Path) -> Path:
    return html_path.with_suffix(".pdf")


def html_to_pdf(
    html_path: Path,
    pdf_path: Path | None = None,
    margin_mm: float = DEFAULT_MARGIN_MM,
) -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "未安装 Playwright。请执行：\n"
            "  pip install playwright\n"
            "  playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(3)

    html_path = html_path.resolve()
    if not html_path.exists():
        raise FileNotFoundError(f"HTML 不存在: {html_path}")

    pdf_path = (pdf_path or default_pdf_path(html_path)).resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    file_uri = html_path.as_uri()
    margin = f"{margin_mm}mm"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(file_uri, wait_until="networkidle", timeout=60000)
        page.wait_for_selector(".resume-container", timeout=30000)
        # Vue 渲染与字体加载
        page.wait_for_timeout(500)

        width_px = page.evaluate(
            """() => {
                const el = document.querySelector('.resume-container');
                return el ? Math.ceil(el.offsetWidth) : 800;
            }"""
        )
        height_px = page.evaluate(
            """() => {
                const body = document.body;
                const html = document.documentElement;
                return Math.ceil(Math.max(
                    body.scrollHeight, body.offsetHeight,
                    html.clientHeight, html.scrollHeight, html.offsetHeight
                ));
            }"""
        )
        height_px = max(height_px, 400)

        page.pdf(
            path=str(pdf_path),
            print_background=True,
            width=f"{width_px}px",
            height=f"{height_px}px",
            margin={"top": margin, "right": margin, "bottom": margin, "left": margin},
            prefer_css_page_size=False,
        )
        browser.close()

    return pdf_path


def export_pdfs_from_paths(html_paths: list[Path], margin_mm: float) -> list[Path]:
    results: list[Path] = []
    for html_path in html_paths:
        results.append(html_to_pdf(html_path, margin_mm=margin_mm))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Export resume HTML to PDF (Playwright)")
    parser.add_argument(
        "html",
        type=Path,
        nargs="*",
        help="HTML file path(s); default: all *.html in output/",
    )
    parser.add_argument("-o", "--output", type=Path, help="PDF output path (single input only)")
    parser.add_argument(
        "--margin",
        type=float,
        default=DEFAULT_MARGIN_MM,
        help="PDF margin in mm (default: 0)",
    )
    args = parser.parse_args()

    if args.html:
        html_paths = [resolve_path(p) for p in args.html]
    else:
        out = project_root() / "output"
        html_paths = sorted(out.glob("*.html"))
        if not html_paths:
            print("未找到 HTML 文件", file=sys.stderr)
            sys.exit(2)

    if args.output and len(html_paths) != 1:
        parser.error("--output 仅适用于单个 HTML 输入")

    pdf_paths: list[Path] = []
    for html_path in html_paths:
        if not html_path.exists():
            print(f"跳过（不存在）: {html_path}", file=sys.stderr)
            continue
        pdf_out = resolve_path(args.output) if args.output else None
        pdf_paths.append(html_to_pdf(html_path, pdf_out, margin_mm=args.margin))

    for p in pdf_paths:
        print(str(p))


if __name__ == "__main__":
    main()
