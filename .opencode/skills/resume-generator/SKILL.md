---
name: resume-generator
description: Parses user resume/CV text into resume.json and renders a minimalist Vue HTML resume. Use when the user provides personal resume info, asks to generate 简历, create resume.json, or render an HTML resume page.
compatibility: opencode
license: MIT
metadata:
  category: document
  workflow: resume
---

# 简历生成器（OpenCode）

完整说明见 `skills/resume-generator/INSTRUCTIONS.md`、`skills/resume-generator/HITL.md`。

## 工作流要点

展示摘要后 **必须询问**：① 主题风格三选一 ② 是否上传头像。未答复前禁止 `finalize` / `render`。

见 `skills/resume-generator/HITL.md`、`AVATAR.md`。
