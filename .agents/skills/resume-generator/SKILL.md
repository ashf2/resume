---
name: resume-generator
description: Parses user resume/CV text into resume.json and renders a minimalist Vue HTML resume. Use when the user provides personal resume info, asks to generate 简历, create resume.json, or render an HTML resume page. Invoke with $resume-generator or when user mentions resume/CV generation.
metadata:
  short-description: Generate HTML resume from user input
---

# 简历生成器（Codex）

完整说明见 `skills/resume-generator/INSTRUCTIONS.md`、`skills/resume-generator/HITL.md`。

## 工作流要点

摘要预览后 **必须询问**主题风格与头像；用户确认三项后再定稿渲染。禁止擅自 default 主题或历史头像。

添加或更新 skill 后需**重启 Codex** 以加载变更。
