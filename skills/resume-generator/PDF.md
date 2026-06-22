# PDF 导出（求职投递格式）

HR 与 ATS 常要求 PDF。在 HTML 渲染完成后，使用 Playwright 无头浏览器加载页面并导出高清 PDF。

## 工作流位置（步骤 6）

```
步骤 5: render_resume.py output/resume.json [--theme ...]
步骤 6: export_pdf.py <html>   # 或使用 render_resume.py --pdf 一步完成
步骤 7: 告知 JSON、HTML、PDF 路径
```

## 依赖安装（首次使用）

```bash
pip install -r requirements.txt
playwright install chromium
```

仅需 Chromium，无需完整浏览器界面。

## 命令

### 与渲染一并导出（推荐）

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json --theme blue-minimal --pdf
```

`--all-themes --pdf` 会为每个主题的 HTML 各生成一份 PDF。

### 单独从 HTML 导出

```bash
python skills/resume-generator/scripts/export_pdf.py output/蒋东海-AI Agent 工程师-blue-minimal.html

# 指定 PDF 路径
python skills/resume-generator/scripts/export_pdf.py output/resume.html -o output/resume.pdf

# 导出 output/ 下全部 HTML
python skills/resume-generator/scripts/export_pdf.py
```

默认输出：与 HTML 同目录、同名 `.pdf` 文件。

## 技术说明

- 工具：**Playwright**（Chromium headless），非 Puppeteer（Node 栈）；效果等同无头浏览器打印。
- `print_background=True`：保留主题背景色与色块。
- 按页面实际宽高导出，避免简历被裁切。
- HTML 依赖 CDN 上的 Vue 3，导出时需联网加载；`networkidle` 后等待 Vue 渲染完成。

## 头像与本地资源

PDF 导出使用 `file://` 打开 HTML。头像等相对路径须能被 HTML 正确引用（`output/avatars/`）。

若 PDF 中头像缺失，可先：

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json --embed-avatar --pdf
```

或将 `setup_avatar.py` 配置好的相对路径保持在 `output/` 目录结构内。

## Agent 交付清单

定稿渲染后，默认执行 PDF 导出（`--pdf`），并向用户返回：

1. `output/resume.json`
2. `output/{姓名}-{职位}[-{主题}].html`
3. `output/{姓名}-{职位}[-{主题}].pdf`

## 故障排除

| 问题 | 处理 |
|------|------|
| `未安装 Playwright` | `pip install playwright && playwright install chromium` |
| 空白 PDF | 检查网络（Vue CDN）；延长等待或重试 |
| 头像不显示 | 使用 `--embed-avatar` 重新渲染并导出 |
