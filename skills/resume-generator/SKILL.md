---
name: resume-generator
description: Parses user resume/CV text into resume.json and renders a minimalist Vue HTML resume. Use when the user provides personal resume info, asks to generate 简历, create resume.json, or render an HTML resume page.
metadata: {"openclaw":{"requires":{"bins":["python"]}}}
---

# 简历生成器（OpenClaw）

技能资源目录：`{baseDir}`。

**用户说明**：[README.md](README.md) · Agent 执行：[INSTRUCTIONS.md](INSTRUCTIONS.md) · [HITL.md](HITL.md)

## 工作流（摘要）

1. 提取 → `output/resume.draft.json` → 校验 → 优化
2. **展示 Markdown 摘要**
3. **【必问】** 用户选择主题：`default` / `blue-minimal` / `classic`（或三种都生成）
4. **【必问】** 用户是否上传头像：图片 / URL / 不要
5. 用户确认内容后 → `finalize_resume.py` → `setup_avatar.py` → `render_resume.py --pdf`

**禁止**在未询问主题与头像前定稿或渲染；**禁止**擅自使用 default 主题或历史头像。

话术见 `{baseDir}/HITL.md`、`{baseDir}/AVATAR.md`。PDF 见 `{baseDir}/PDF.md`。

## 快速命令

```bash
python {baseDir}/scripts/preview_resume.py --draft
python {baseDir}/scripts/finalize_resume.py
python {baseDir}/scripts/setup_avatar.py --hide -r output/resume.json
python {baseDir}/scripts/render_resume.py output/resume.json --pdf
```