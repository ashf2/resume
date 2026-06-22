# resume.json 数据规范

标准骨架：`templates/resume.json`

HTML 模板：`templates/resume.html`（Vue 3 + CDN，简约白底卡片布局）

## 顶层字段

| 字段 | 说明 |
|------|------|
| `titleNameMap` | 各模块在页面上的章节标题 |
| `avatar` | `src` 头像地址；`hidden: true` 隐藏。见 [AVATAR.md](AVATAR.md) |
| `profile` | 姓名、联系方式、`position` 意向职位 |
| `educationList` | 教育背景 |
| `workExpList` | 工作经历 / 实习 |
| `projectList` | 项目经验 |
| `skillList` | 个人技能 |
| `awardList` | 更多信息（JSON 可存，HTML 未展示） |
| `workList` | 个人作品（JSON 可存，HTML 未展示） |
| `aboutme` | 个人评价 |
| `theme` | 见下方主题字段 |

## theme（简历主题）

| 字段 | 说明 |
|------|------|
| `id` | `default` / `blue-minimal` / `classic` |
| `name` | 主题中文名（可选，脚本从 themes.json 补全） |
| `color` | 主色（脚本从预设补全） |
| `tagColor` | 标签色 |
| `pageBg` / `cardBg` / `textMain` / `textLight` / `lineColor` | 页面与文字色（可选） |

主题目录：`templates/themes.json`

| id | 名称 |
|----|------|
| `default` | 系统默认 |
| `blue-minimal` | 蓝色简约 |
| `classic` | 通用美观 |

## profile

| 字段 | 说明 |
|------|------|
| `name` | 姓名 |
| `email` | 邮箱 |
| `mobile` | 手机 |
| `github` | 链接可带说明，URL 取第一个空格前 |
| `zhihu` | 知乎链接 |
| `workExpYear` | 工作年限（可选） |
| `position` | 意向职位，显示在页眉姓名下方 |

## educationList[]

`edu_time`, `school`, `major`, `academic_degree`

## workExpList[]

`company_name`, `department_name`, `work_time`（结束 `null` 为至今）, `work_desc`

## projectList[]

`project_name`, `project_role`, `project_time`, `project_desc`, `project_content`

## aboutme

`{ "aboutme_desc": "..." }`

## HTML 章节顺序

页眉 → 教育背景 → 专业技能 → 工作/实习 → 项目经验 → 个人评价

## 内容智能优化（步骤 2b）

可选 JD 输入 + STAR 润色 + 技能按 JD 重排。详见 [OPTIMIZATION.md](OPTIMIZATION.md)。

```bash
python skills/resume-generator/scripts/save_jd.py -f jd.txt --title "岗位"
python skills/resume-generator/scripts/analyze_star.py output/resume.draft.json --json
python skills/resume-generator/scripts/jd_match.py output/resume.draft.json --apply --write
```

## JSON 校验（步骤 2.5，草稿）

防止 LLM 提取时出现字段遗漏或类型错误。详见 [VALIDATION.md](VALIDATION.md)。

草稿路径：`output/resume.draft.json`

```bash
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json --normalize --write
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json
```

## HITL 确认（步骤 3，定稿前）

**Agent 必须询问**用户：① 简历主题风格 ② 是否上传头像。未明确答复前不得定稿渲染。

详见 [HITL.md](HITL.md)、[AVATAR.md](AVATAR.md)。

```bash
python skills/resume-generator/scripts/preview_resume.py --draft
python skills/resume-generator/scripts/finalize_resume.py
```

用户确认前不得写入 `output/resume.json` 或渲染 HTML。

## 渲染与 PDF 导出

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json --pdf
python skills/resume-generator/scripts/render_resume.py output/resume.json --theme blue-minimal --pdf
python skills/resume-generator/scripts/render_resume.py output/resume.json --all-themes --pdf
python skills/resume-generator/scripts/export_pdf.py output/xxx.html
```

默认输出：`output/{姓名}-{意向职位}.html` 与同名 `.pdf`。详见 [PDF.md](PDF.md)。
