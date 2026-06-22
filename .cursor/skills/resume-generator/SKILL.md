---
name: resume-generator
description: Parses user resume/CV text into resume.json and renders a minimalist Vue HTML resume. Use when the user provides personal resume info, asks to generate 简历, create resume.json, or render an HTML resume page.
---

# 简历生成器（Cursor）

完整说明见 `skills/resume-generator/README.md`；Agent 细则见 `INSTRUCTIONS.md`、`HITL.md`。

## 工作流要点

1. 写入 `output/resume.draft.json` → 校验 → 展示摘要
2. **必须询问**用户选择简历风格（三选一）与是否上传头像
3. 用户确认后定稿、配置头像、渲染 HTML 并**导出 PDF**（`--pdf`）

见 `skills/resume-generator/PDF.md`
