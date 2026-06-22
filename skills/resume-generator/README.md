# 简历生成器 Skill 说明

将自然语言、Markdown 或零散文本中的简历信息，自动提取为结构化数据，经校验与人机确认后，生成可直接投递的 **JSON + HTML + PDF** 简历。

---

## 功能概览

| 能力 | 说明 |
|------|------|
| **信息提取** | 从自由文本整理为 `resume.json` 标准结构 |
| **内容优化** | 可选 JD 匹配重排技能；STAR 原则润色单薄描述 |
| **JSON Schema 校验** | 拦截字段遗漏、类型错误（数组误解析为字符串等） |
| **HITL 人机确认** | 定稿前展示 Markdown 摘要，支持对话微调 |
| **主题风格** | 三种视觉主题，用户必选 |
| **头像** | 支持上传 / URL / 不显示，用户必答 |
| **HTML 渲染** | Vue 3 简约排版，与 `templates/resume.html` 一致 |
| **PDF 导出** | Playwright 无头浏览器打印，适配 HR / ATS |

---

## 你会得到什么

定稿后，`output/` 目录下通常包含：

| 文件 | 说明 |
|------|------|
| `resume.json` | 结构化简历数据（可二次编辑） |
| `{姓名}-{意向职位}[-{主题}].html` | 浏览器预览用 |
| `{姓名}-{意向职位}[-{主题}].pdf` | 求职投递用 |
| `resume.draft.json` | 提取与微调阶段的草稿（定稿前） |
| `avatars/` | 头像图片（若用户选择上传） |

---

## 快速开始（使用者）

1. 在 Cursor / Codex / OpenCode / OpenClaw 中打开本仓库。
2. 向 Agent 发送简历信息，例如：

   > 这是我的简历，请帮我生成一份简历。

3. Agent 会：
   - 整理内容并展示**摘要预览**
   - **询问**你选择的**简历风格**（三选一）
   - **询问**是否**上传头像**
4. 你确认内容、风格、头像后，Agent 生成 HTML 与 PDF。
5. 打开 `output/` 下的 HTML 预览，PDF 直接投递。

也可在对话中继续微调，例如：

- 「把第二段实习改精炼一点」
- 「意向职位改成大模型应用开发工程师」

---

## 完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 用户提供简历文本 + 【可选】目标岗位 JD                      │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 提取 → output/resume.draft.json                          │
│ 2b. 内容优化：STAR 润色 + JD 技能重排（可选）                 │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2.5 校验 — 信息缺失则追问用户，不进入下一步                    │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. HITL：Markdown 摘要 + 【必问】主题风格 + 【必问】头像       │
│     用户可对话微调 draft                                       │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 用户确认 → finalize → 配置头像 → render HTML → 导出 PDF   │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 交付 JSON、HTML、PDF 路径                                 │
└─────────────────────────────────────────────────────────────┘
```

**重要**：Agent **不得**在用户未选择主题、未答复头像前定稿或渲染；**不得**擅自使用 `default` 主题或历史头像配置。

---

## 简历主题（三选一）

| id | 名称 | 风格 |
|----|------|------|
| `default` | 系统默认 | 蓝绿配色、白底卡片 |
| `blue-minimal` | 蓝色简约 | 冷色极简、浅蓝背景 |
| `classic` | 通用美观 | 商务暖灰、章节色条 |

配置详情：`templates/themes.json`

回复示例：`风格 2` 或 `blue-minimal`；也可回复「三种都生成」。

---

## 头像

每次生成须三选一：

1. **上传图片** — 对话中发图或提供本地路径  
2. **提供 URL** — 公网图片链接  
3. **不需要头像**

---

## 内容智能优化（可选）

| 功能 | 何时使用 | 文档 |
|------|----------|------|
| **JD 匹配** | 用户提供目标岗位描述 | [OPTIMIZATION.md](OPTIMIZATION.md) |
| **STAR 润色** | 工作/项目描述过短时自动扩写 | [OPTIMIZATION.md](OPTIMIZATION.md) |

---

## 依赖安装

```bash
# 在项目根目录
pip install -r requirements.txt

# PDF 导出（首次）
playwright install chromium
```

| 依赖 | 用途 |
|------|------|
| Python 3 | 运行脚本 |
| `jsonschema` | 严格 JSON 校验（可选但推荐） |
| `playwright` | HTML → PDF |
| 网络 | HTML 模板加载 Vue 3 CDN；PDF 导出时需联网 |

---

## 命令速查（项目根目录）

所有路径相对于仓库根目录 `resume/`。

### 常用一条龙（定稿后）

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json --theme blue-minimal --pdf
```

### 分步执行

```bash
# 草稿校验
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json

# 摘要预览
python skills/resume-generator/scripts/preview_resume.py --draft

# 定稿
python skills/resume-generator/scripts/finalize_resume.py

# 头像
python skills/resume-generator/scripts/setup_avatar.py "图片路径或URL" -r output/resume.json
python skills/resume-generator/scripts/setup_avatar.py --hide -r output/resume.json

# 渲染 + PDF
python skills/resume-generator/scripts/render_resume.py output/resume.json --pdf

# 仅从 HTML 导出 PDF
python skills/resume-generator/scripts/export_pdf.py output/xxx.html
```

### 内容优化

```bash
python skills/resume-generator/scripts/save_jd.py -f jd.txt --title "岗位名称"
python skills/resume-generator/scripts/analyze_star.py output/resume.draft.json --json
python skills/resume-generator/scripts/jd_match.py output/resume.draft.json --apply --write
```

### 查看主题列表

```bash
python skills/resume-generator/scripts/render_resume.py --list-themes
```

---

## 目录结构

```
skills/resume-generator/
├── README.md              # 本说明（用户向）
├── SKILL.md               # Agent 入口（OpenClaw 等）
├── INSTRUCTIONS.md        # Agent 执行清单
├── HITL.md                # 人机确认、主题与头像必问
├── VALIDATION.md          # 校验与反向追问
├── OPTIMIZATION.md        # JD 匹配与 STAR 润色
├── PDF.md                 # PDF 导出
├── AVATAR.md              # 头像处理
├── reference.md           # resume.json 字段规范
├── schemas/resume.schema.json
├── data/jd_keywords.json
├── examples/resume.example.json
└── scripts/
    ├── validate_resume.py
    ├── preview_resume.py
    ├── finalize_resume.py
    ├── setup_avatar.py
    ├── render_resume.py
    ├── export_pdf.py
    ├── save_jd.py
    ├── jd_match.py
    ├── analyze_star.py
    └── optimize_content.py

templates/
├── resume.html            # HTML 模板
├── resume.json            # 数据骨架
└── themes.json            # 主题配置

output/                    # 生成结果
```

---

## 多平台安装

| 平台 | 技能路径 |
|------|----------|
| **Cursor** | `.cursor/skills/resume-generator/SKILL.md` |
| **Codex** | `.agents/skills/resume-generator/SKILL.md` |
| **OpenCode** | `.opencode/skills/resume-generator/SKILL.md` |
| **OpenClaw** | `skills/resume-generator/`（完整包，含 `{baseDir}`） |

仓库根目录 [README.md](../README.md) 中有各平台详细安装步骤。

---

## 文档索引（Agent 深入阅读）

| 文档 | 读者 | 内容 |
|------|------|------|
| [INSTRUCTIONS.md](INSTRUCTIONS.md) | Agent | 逐步执行清单 |
| [HITL.md](HITL.md) | Agent | 摘要预览、主题/头像必问、确认门槛 |
| [VALIDATION.md](VALIDATION.md) | Agent | Schema 校验、缺失追问话术 |
| [OPTIMIZATION.md](OPTIMIZATION.md) | Agent | JD 匹配、STAR 润色规则 |
| [AVATAR.md](AVATAR.md) | Agent | 头像收集与脚本用法 |
| [PDF.md](PDF.md) | Agent / 用户 | PDF 导出与排错 |
| [reference.md](reference.md) | Agent | `resume.json` 字段说明 |

---

## 示例

```bash
python skills/resume-generator/scripts/render_resume.py \
  skills/resume-generator/examples/resume.example.json \
  -o output/example-resume.html --pdf
```

---

## 常见问题

**Q：PDF 导出失败，提示未安装 Playwright？**  
A：执行 `pip install playwright` 与 `playwright install chromium`。

**Q：PDF 里头像不显示？**  
A：使用 `--embed-avatar --pdf` 重新渲染，或确认 `output/avatars/` 路径正确。

**Q：Agent 直接生成了 HTML，没问我主题？**  
A：应要求 Agent 遵循 `HITL.md`；定稿前必须询问主题与头像。

**Q：可以只改内容不重新选主题吗？**  
A：可以。对话说明修改项，Agent 更新 draft 后重新校验即可；主题与头像选择仍记录在 draft 中。

---

## 许可证

技能与模板可自由用于个人简历生成。
