# Resume — 多平台 AI 简历生成技能

技能完整说明：**[skills/resume-generator/README.md](skills/resume-generator/README.md)**

从自然语言或现有简历文本提取信息，生成 `resume.json`，并渲染与 `templates/resume.html` 一致的简约风格 HTML 简历，支持导出 PDF。

## 仓库结构

```
resume/
├── templates/
│   ├── resume.html          # Vue 3 简历页面模板
│   └── resume.json          # JSON 数据骨架
├── skills/resume-generator/ # 技能资源包（脚本、示例、说明）
│   ├── README.md            # Skill 使用说明（推荐阅读）
│   ├── SKILL.md             # OpenClaw 完整技能（含 {baseDir}）
│   ├── INSTRUCTIONS.md
│   ├── HITL.md              # 人机确认与 Markdown 预览
│   ├── OPTIMIZATION.md      # JD 匹配与 STAR 润色
│   ├── VALIDATION.md        # JSON 校验与反向追问
│   ├── data/jd_keywords.json
│   ├── scripts/save_jd.py
│   ├── scripts/analyze_star.py
│   ├── scripts/jd_match.py
│   ├── scripts/export_pdf.py
│   ├── PDF.md                 # PDF 导出说明
│   ├── reference.md
│   ├── schemas/resume.schema.json
│   ├── scripts/preview_resume.py
│   ├── scripts/finalize_resume.py
│   ├── scripts/render_resume.py
│   ├── scripts/validate_resume.py
│   └── examples/resume.example.json
├── .cursor/skills/resume-generator/SKILL.md
├── .opencode/skills/resume-generator/SKILL.md
├── .agents/skills/resume-generator/SKILL.md
├── .openclaw/skills/resume-generator/SKILL.md
└── output/                  # 生成的 resume.json 与 HTML
```

## 快速使用（任意平台）

1. 向 AI 提供个人简历信息；**可选**提供目标岗位 JD。
2. Agent 写入草稿、展示内容摘要；你可对话微调。
3. **Agent 必须询问**你选择的**主题风格**与是否**上传头像**（见 `HITL.md`）。
4. 确认后定稿、渲染 HTML，并**自动导出 PDF**（求职投递格式）：

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json --pdf
python skills/resume-generator/scripts/render_resume.py output/resume.json --theme blue-minimal --pdf
```

5. 打开 `output/` 下 HTML 预览，PDF 可直接投递。

### 内容优化与校验

```bash
python skills/resume-generator/scripts/save_jd.py -f jd.txt --title "后端开发"
python skills/resume-generator/scripts/analyze_star.py output/resume.draft.json --json
python skills/resume-generator/scripts/jd_match.py output/resume.draft.json --apply --write
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json
python skills/resume-generator/scripts/preview_resume.py --draft
python skills/resume-generator/scripts/finalize_resume.py
```

详见 `skills/resume-generator/OPTIMIZATION.md`、`HITL.md`、`VALIDATION.md`。

## 简历主题

| id | 名称 | 风格 |
|----|------|------|
| `default` | 系统默认 | 当前蓝绿简约模板 |
| `blue-minimal` | 蓝色简约 | 冷色极简、浅蓝背景 |
| `classic` | 通用美观 | 商务暖灰、章节色条 |

配置文件：`templates/themes.json`

## 头像（定稿前必问）

Agent **每次生成**都会询问是否添加头像，不得跳过。支持：对话上传、本地路径、图片 URL。

```bash
python skills/resume-generator/scripts/setup_avatar.py "<图片路径或URL>" -r output/resume.json
python skills/resume-generator/scripts/render_resume.py output/resume.json
```

图片保存至 `output/avatars/`。详见 `skills/resume-generator/AVATAR.md`。

---

## Cursor

### 安装

将本仓库作为 Cursor 项目打开即可。技能路径：

`.cursor/skills/resume-generator/SKILL.md`

### 使用

1. 在 Cursor Agent 对话中输入简历信息，例如：「这是我的简历，请帮我生成」。
2. Agent 会自动匹配 `resume-generator` skill（或手动提及「用 resume skill」）。
3. 确认 `output/resume.json` 与 HTML 路径后，在浏览器打开 HTML 预览。

### 说明

- Cursor 从 `.cursor/skills/` 发现技能。
- 脚本与模板在 `skills/resume-generator/` 与 `templates/`，无需额外安装。

---

## OpenCode

### 安装

本仓库已包含：

`.opencode/skills/resume-generator/SKILL.md`

克隆仓库后，在项目目录启动 OpenCode 即可发现技能。

全局安装（可选）：

```bash
mkdir -p ~/.config/opencode/skills
cp -r skills/resume-generator ~/.config/opencode/skills/resume-generator
```

（全局副本需自行保证能访问本仓库的 `templates/` 与 `output/`，推荐在仓库内使用。）

### 使用

1. 在 OpenCode 中打开本仓库。
2. 输入简历信息，或让 Agent 加载 `resume-generator` skill。
3. Agent 整合 `output/resume.json` 并执行渲染命令。
4. 用浏览器打开生成的 HTML。

### 说明

- OpenCode 同时兼容 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/`。
- `name` 须与目录名一致：`resume-generator`。

---

## Codex（OpenAI Codex CLI / IDE）

### 安装

本仓库已包含：

`.agents/skills/resume-generator/SKILL.md`

用户级安装（可选）：

```bash
mkdir -p ~/.agents/skills
cp -r skills/resume-generator ~/.agents/skills/resume-generator
```

### 使用

1. 在 Codex 中打开本仓库。
2. 输入简历信息，或使用 `$resume-generator` / `/skills` 显式调用技能。
3. Agent 生成 `output/resume.json` 并运行渲染脚本。
4. **修改 skill 后需重启 Codex** 才会重新加载。

### 说明

- Codex 遵循 [Agent Skills](https://agentskills.io) 开放格式。
- 技能发现路径：`.agents/skills/`（项目）或 `~/.agents/skills/`（用户）。

---

## OpenClaw

### 安装

**方式 A（推荐）**：将本仓库作为 OpenClaw 工作区，并链接完整技能包：

```bash
# 在仓库根目录
ln -s "$(pwd)/skills/resume-generator" ~/.openclaw/workspace/skills/resume-generator
```

**方式 B**：仅使用项目内说明入口：

`.openclaw/skills/resume-generator/SKILL.md`

（脚本仍在 `skills/resume-generator/scripts/`，需在本仓库根目录执行命令。）

### 使用

1. 将工作区指向本仓库（或已链接 skill 的环境）。
2. 新开会话：`/new`，或 `openclaw gateway restart`。
3. 验证：`openclaw skills list` 应出现 `resume-generator`。
4. 在对话中提供简历信息，或 slash 调用相关 skill。
5. 打开 `output/` 下生成的 HTML。

### 说明

- 完整技能包使用 `{baseDir}` 引用脚本：`skills/resume-generator/SKILL.md`。
- `metadata.openclaw.requires.bins` 要求系统已安装 `python`。
- `description` 是 OpenClaw 判断是否启用技能的主要依据，请保持清晰。

---

## resume.json 字段摘要

| 字段 | 说明 |
|------|------|
| `profile.position` | 意向职位（页眉展示） |
| `profile.name` / `mobile` / `email` | 基本信息 |
| `educationList` | 教育背景 |
| `workExpList` | 工作 / 实习 |
| `projectList` | 项目经验 |
| `skillList` | 专业技能 |
| `aboutme.aboutme_desc` | 个人评价 |
| `theme` | 主题色 |

完整说明：`skills/resume-generator/reference.md`

## 示例

```bash
python skills/resume-generator/scripts/render_resume.py skills/resume-generator/examples/resume.example.json -o output/example-resume.html
```

## 依赖

- Python 3
- 推荐：`pip install -r requirements.txt`（`jsonschema`、`playwright`）
- PDF 首次使用：`playwright install chromium`
- 浏览器（预览 HTML）
- HTML 模板依赖 CDN 上的 Vue 3（`unpkg.com`）

## 许可证

技能与模板可自由用于个人简历生成。
