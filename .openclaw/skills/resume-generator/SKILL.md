---
name: resume-generator
description: Parses user resume/CV text into resume.json and renders a minimalist Vue HTML resume. Use when user provides resume info, asks to generate 简历, or render HTML resume.
metadata: {"openclaw":{"requires":{"bins":["python"]}}}
---

# 简历生成器（OpenClaw 项目入口）

本文件为项目内快捷入口。完整技能包（脚本、示例、说明）在 `skills/resume-generator/`。

安装：将 `skills/resume-generator` 目录复制或软链到 OpenClaw 工作区：

```bash
ln -s "$(pwd)/skills/resume-generator" ~/.openclaw/workspace/skills/resume-generator
```

然后执行 `/new` 或 `openclaw gateway restart`，用 `openclaw skills list` 验证。

## 快速命令（在仓库根目录）

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json
```

工作区内的 skill 副本可使用：

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json
```

（脚本路径相对于本仓库根目录，需将本仓库作为 OpenClaw 工作区打开。）

详细说明：`skills/resume-generator/INSTRUCTIONS.md`

**HITL（必问主题 + 必问头像）**：`skills/resume-generator/HITL.md`

定稿前必须询问主题风格与是否上传头像。定稿后 `render_resume.py --pdf` 生成 HTML + PDF。见 `PDF.md`。

```bash
python skills/resume-generator/scripts/save_jd.py -f jd.txt --title "岗位"
python skills/resume-generator/scripts/analyze_star.py output/resume.draft.json --json
python skills/resume-generator/scripts/jd_match.py output/resume.draft.json --apply --write
```
