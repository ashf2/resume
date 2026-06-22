# JSON 校验与反向追问

防止 LLM 提取简历信息时出现字段遗漏、类型错误或格式幻觉。

## 拦截规则（校验未通过则禁止继续）

**在步骤 2 写入 `output/resume.draft.json` 之后**，必须先运行校验。**校验失败时：**

1. **不得**进入主题选择、头像、渲染 HTML 等后续步骤
2. **必须**向用户输出缺失/错误清单（使用下方话术）
3. 等待用户补充后更新 JSON，**重新校验**，通过后再继续

## 校验命令（步骤 2 之后强制执行）

```bash
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json
```

自动修正常见格式问题后再校验（字符串误解析为数组、时间字符串等）：

```bash
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json --normalize --write
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json
```

JSON 格式输出（便于 Agent 解析）：

```bash
python skills/resume-generator/scripts/validate_resume.py output/resume.draft.json --json
```

Schema 文件：`skills/resume-generator/schemas/resume.schema.json`

安装 JSON Schema 校验（推荐）：

```bash
pip install -r requirements.txt
```

未安装 `jsonschema` 时仍执行业务规则校验（必填项、数组类型等）。

## 必填业务字段

| 字段 | 要求 |
|------|------|
| `profile.name` | 非空 |
| `profile.mobile` 或 `profile.email` | 至少一项非空 |
| `profile.position` | 非空（意向职位） |
| `educationList` | 至少 1 条，含 `school`、`academic_degree`、`edu_time` 数组 |
| `workExpList` 或 `projectList` | 至少一方非空 |

## 类型检查

以下字段**必须是数组**，不能是字符串或单个对象：

`educationList`, `workExpList`, `projectList`, `skillList`, `awardList`, `workList`

时间字段必须是数组：

- `educationList[].edu_time` — 如 `["2022.09", "2026.07"]` 或 `["2018.06", null]`
- `workExpList[].work_time` — 同上

## 反向追问话术（校验失败时原样发给用户）

```
您的输入中以下核心信息缺失或格式有误，请补充后我再为您生成排版：

- （逐条列出 validate_resume.py 输出的错误）

请补充上述内容后告诉我，我会更新 resume.json 并继续生成简历。
```

示例：

> 您的输入中以下核心信息缺失或格式有误，请补充后我再为您生成排版：
>
> - 必填：联系方式 — 至少填写手机号或邮箱
> - 教育经历[1]：缺少就读时间（edu_time，应为数组如 "2022.09", "2026.07"）
>
> 请补充上述内容后告诉我，我会更新 resume.json 并继续生成简历。

## 与渲染脚本联动

`render_resume.py` 默认在渲染前再次校验；失败则退出且不生成 HTML：

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json
```

仅调试时可跳过（不推荐）：

```bash
python skills/resume-generator/scripts/render_resume.py output/resume.json --skip-validation
```

## Agent 工作流插入点

```
步骤 2：写入 output/resume.draft.json
步骤 2.5：validate → 失败则追问，停止
步骤 3：HITL 预览与微调（见 HITL.md）
步骤 4：用户确认 → finalize_resume.py
步骤 5：render_resume.py
```

定稿前校验草稿；`render_resume.py` 仅针对 `output/resume.json`。
