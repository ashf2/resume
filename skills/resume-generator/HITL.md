# Human-in-the-loop（HITL）确认机制

在写入不可逆的最终文件（`output/resume.json`、HTML）之前，让用户审阅、修改中间态数据，并**明确选择简历风格与头像**。

## 核心原则

| 阶段 | 文件 | 说明 |
|------|------|------|
| **中间态** | `output/resume.draft.json` | 提取与微调阶段只读写此文件 |
| **最终态** | `output/resume.json` | 用户明确确认后才写入 |
| **预览** | 对话内 Markdown 摘要 | 步骤 3 展示 |

**禁止**：在用户完成下方三项确认前运行 `finalize_resume.py`、`render_resume.py` 或写入 `output/*.html`。

## 三项确认门槛（缺一不可）

| # | 确认项 | 用户须明确答复 | Agent 禁止行为 |
|---|--------|----------------|----------------|
| 1 | **内容** | 核对摘要，可微调；满意或说「确认生成」 | 不得跳过摘要预览 |
| 2 | **主题风格** | 从三种主题中**选一** | **禁止**擅自使用 `default` 或沿用旧配置 |
| 3 | **头像** | **三选一**：上传图片 / 提供 URL / 不要头像 | **禁止**沿用历史 `avatar` 或默认隐藏而不询问 |

未获得主题与头像的明确答复时，即使用户说「生成简历」也须先完成询问，**停止在 draft 阶段**。

## 工作流插入点

```
步骤 2：提取 → 优化 → output/resume.draft.json
步骤 2.5：validate_resume.py
步骤 3：【HITL】Markdown 摘要 + 【必问】主题风格 + 【必问】头像
步骤 3 循环：内容微调 → 更新 draft
步骤 4：三项均确认后 → finalize_resume.py → setup_avatar（按用户选择）→ render
```

## 步骤 3：摘要预览

```bash
python skills/resume-generator/scripts/preview_resume.py --draft
# 或
python skills/resume-generator/scripts/preview_resume.py --draft -o output/resume.preview.md
```

展示摘要后，**必须紧接着**发出主题与头像询问（见下方话术），不要只展示摘要就定稿。

## 步骤 3：【必问】主题风格（三选一）

向用户展示表格并**等待选择**（配置见 `templates/themes.json`）：

| id | 名称 | 风格说明 |
|----|------|----------|
| `default` | 系统默认 | 蓝绿配色、白底卡片，当前仓库默认简约风 |
| `blue-minimal` | 蓝色简约 | 冷色极简、浅蓝背景、留白更多 |
| `classic` | 通用美观 | 商务暖灰、章节色条、柔和阴影 |

**Agent 话术（必须发送）**：

```
请选择简历的视觉风格（回复编号或 id 即可）：

1. default — 系统默认（蓝绿简约）
2. blue-minimal — 蓝色简约（冷色极简）
3. classic — 通用美观（商务暖灰）

您也可以回复「三种都生成」一次性输出三个 HTML。
```

用户选定后，将 `theme.id` 写入 **draft**（定稿前勿渲染）。若用户选「三种都生成」，定稿后使用：

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json --all-themes
```

## 步骤 3：【必问】头像

**必须主动询问**，详见 [AVATAR.md](AVATAR.md)。不可跳过。

**Agent 话术（必须发送）**：

```
是否需要添加头像照片？

1. 上传图片：在对话中发送照片，或提供本地路径（如 D:\photo.jpg）
2. 提供链接：公网图片 URL（如 GitHub 头像）
3. 不需要：简历不显示头像

请回复 1 / 2 / 3，或直接把图片发给我。
```

| 用户选择 | Agent 动作 |
|----------|------------|
| 上传 / 路径 | 定稿后 `setup_avatar.py "<路径>" -r output/resume.json` |
| URL | 定稿后 `setup_avatar.py "<URL>" -r output/resume.json` |
| 不需要 | 定稿后 `setup_avatar.py --hide -r output/resume.json` |

**禁止**：未询问时写入历史头像路径；未询问时默认 `hidden: true` 并直接渲染。

## 步骤 3 合并引导话术（推荐一次发送）

```
以上是为您整理的简历内容摘要，请先核对。

【内容】如需修改请直接说明；内容满意可回复「确认内容」。

【风格】请选择简历主题：
  1. default（系统默认）  2. blue-minimal（蓝色简约）  3. classic（通用美观）
  或回复「三种都生成」

【头像】是否需要头像？
  1. 上传/提供图片路径  2. 提供图片链接  3. 不需要头像

三项都确认后（或回复「确认生成」并附带主题与头像选择），我将生成最终 HTML。
```

## 对话微调规则（Agent）

1. **只改 draft**；微调期间不得 finalize / render。
2. 实质性修改后重新 `validate_resume.py`。
3. 润色不得编造技术与数据（见 `OPTIMIZATION.md`）。

## 用户确认后（步骤 4–5）

**仅当**内容、主题、头像均已明确：

```bash
python skills/resume-generator/scripts/finalize_resume.py
python skills/resume-generator/scripts/setup_avatar.py ...   # 按用户头像选择
python skills/resume-generator/scripts/render_resume.py output/resume.json --pdf
# 或 --theme blue-minimal / --all-themes --pdf
```

PDF 导出见 [PDF.md](PDF.md)。

## 不可逆操作清单（三项确认前禁止）

- 写入或覆盖 `output/resume.json`
- 运行 `render_resume.py`
- 运行 `setup_avatar.py` 写入最终 `resume.json`（draft 阶段可设 `avatar.hidden: true` 占位）

草稿 `resume.draft.json` 可随时覆盖。
