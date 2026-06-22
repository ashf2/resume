# 简历生成器 — 执行说明

从用户输入提取信息 → 优化 → 校验 → **HITL** → 定稿 → 渲染 HTML → **导出 PDF**。

请先阅读 `HITL.md`、`PDF.md`、`AVATAR.md`、`OPTIMIZATION.md`、`VALIDATION.md`。

## 工作流程

```
- [ ] 1. 阅读 templates、schemas、HITL.md、PDF.md
- [ ] 1b. 【可选】目标岗位 JD → save_jd.py
- [ ] 2. 整合 output/resume.draft.json
- [ ] 2b. STAR 润色 + JD 匹配
- [ ] 2.5 validate_resume.py
- [ ] 3. 【HITL】摘要 + 【必问】主题 + 【必问】头像
- [ ] 4. finalize_resume.py → setup_avatar.py
- [ ] 5. render_resume.py（建议加 --pdf）
- [ ] 6. export_pdf.py（若步骤 5 未加 --pdf）
- [ ] 7. 告知 JSON、HTML、PDF 路径
```

## 渲染 HTML + PDF（步骤 5–6）

```bash
# 推荐：HTML 与 PDF 一步完成
python skills/resume-generator/scripts/render_resume.py output/resume.json --theme blue-minimal --pdf

# 仅从已有 HTML 导出 PDF
python skills/resume-generator/scripts/export_pdf.py output/姓名-职位.html
```

PDF 依赖 Playwright，首次需：

```bash
pip install -r requirements.txt
playwright install chromium
```

详见 [PDF.md](PDF.md)。

## 必问项

主题风格与头像：见 `HITL.md`、`AVATAR.md`。

## 质量检查

- 已询问主题与头像
- draft 校验通过
- 已向用户提供 JSON、HTML、**PDF** 路径
