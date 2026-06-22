# 内容智能优化（Content Optimization）

简历 Agent 不仅是数据「搬运工」，更是「润色师」。在步骤 2 整合数据时执行本节点（可与提取合并为一步）。

## 步骤 1：可选输入 — 目标岗位 JD

在收集用户简历信息时，**主动询问**（可选）：

> 是否有目标岗位的招聘描述（JD）？提供后我会按岗位要求调整技能排序，并强化相关经历的表述。

用户提供后保存：

```bash
# 从文件
python skills/resume-generator/scripts/save_jd.py -f path/to/jd.txt --title "后端开发工程师"

# 从对话粘贴的文本
python skills/resume-generator/scripts/save_jd.py "岗位要求：熟悉 Java、Spring Boot…" --title "后端开发"

# 写入 stdin
python skills/resume-generator/scripts/save_jd.py --stdin --title "AI Agent 工程师"
```

生成文件：

| 文件 | 说明 |
|------|------|
| `output/job.jd.txt` | 原始 JD 文本 |
| `output/job.context.json` | 提取的关键词、主导技术方向（cluster） |

无 JD 时跳过 JD 匹配，仍可对单薄描述做 STAR 润色。

---

## 步骤 2：内容优化节点（整合数据时）

在写入 `output/resume.draft.json` **之前或之后立即执行**（仍在 HITL 之前）：

```
2a. 提取结构化字段 → 草稿 JSON
2b. STAR 润色（Agent + analyze_star.py 报告）
2c. JD 匹配重排（若有 JD）
2d. validate_resume.py
```

### 2b. STAR 原则扩写

**目标**：将单薄的工作/项目描述扩写为隐含 STAR（情境、任务、行动、结果）的专业要点，并尽量提取或合理呈现数据指标。

**Agent 流程**：

1. 运行分析脚本，获取待润色清单：

```bash
python skills/resume-generator/scripts/analyze_star.py output/resume.draft.json --json
# 或 Markdown 报告
python skills/resume-generator/scripts/analyze_star.py output/resume.draft.json -o output/star.report.md
```

2. 对 `findings` 中每一项，使用其中的 `star_prompt` 作为扩写指引（由大模型执行）。
3. 将扩写结果写回对应 JSON 路径（`workExpList[i].work_desc` 或 `projectList[i].project_content`）。
4. **诚信约束**：
   - 不得编造用户未提及的技术栈、项目或公司。
   - 数字指标：优先使用用户原文中的数据；若无，可用「显著提升」「保障稳定性」等定性表述，**禁止虚构百分比**。
   - 润色后须仍能通过用户 HITL 确认（步骤 3）。

**STAR 写法参考（每条要点隐含四要素，不必写 S/T/A/R 标签）**：

| 要素 | 简历中的体现 |
|------|----------------|
| Situation 情境 | 业务背景、规模、痛点（如「校园餐饮日均千级访问」） |
| Task 任务 | 你的职责与目标（如「负责订单全链路实时推送」） |
| Action 行动 | 具体技术方案与协作（如「WebSocket + Redis 会话同步」） |
| Result 结果 | 可量化或定性成果（如「响应速度提升 40%」「保障发版稳定」） |

**扩写前 vs 扩写后示例**：

- 原文：`参与后端 API 开发，对接第三方支付。`
- 润色后（若用户原文含 Spring/Redis 等）：
  - `负责农产品融销平台后端 API 开发，对接第三方支付与统一认证服务`
  - `基于 Spring Boot 实现热门商品缓存策略，结合 Redis 降低数据库读压力`
  - `配合团队完成华为云部署与跨部门联调，保障支付链路按时上线`

### 2c. 动态 JD 匹配

当存在 `output/job.jd.txt` 时：

```bash
# 查看匹配报告
python skills/resume-generator/scripts/jd_match.py output/resume.draft.json --json

# 应用技能重排并写回草稿
python skills/resume-generator/scripts/jd_match.py output/resume.draft.json --apply --write

# 可选：同时重排工作与项目（JD 相关度高的置顶）
python skills/resume-generator/scripts/jd_match.py output/resume.draft.json --apply --write --reorder-work --reorder-projects
```

**行为说明**：

- `skillList`：按与 JD 关键词重合度**降序重排**（如 JD 强调 Java/JVM，则 Java 相关技能块置顶）。
- `workExpList` / `projectList`：仅在显式加 `--reorder-work` / `--reorder-projects` 时重排。
- 若 `job.context.json` 中 `title` 与 `profile.position` 不一致，Agent 可询问用户是否对齐意向职位。

**关键词数据**：`skills/resume-generator/data/jd_keywords.json`（技术词表与方向 cluster，可按需扩展）。

---

## 一键优化检查（可选）

```bash
python skills/resume-generator/scripts/optimize_content.py output/resume.draft.json
```

依次执行：STAR 分析（JSON）+ JD 匹配报告（若存在 JD）。不自动改文件，供 Agent 决策。

---

## 与其他节点的关系

| 节点 | 关系 |
|------|------|
| VALIDATION | 优化后必须重新校验 draft |
| HITL | 润色与重排结果在步骤 3 摘要中展示，用户可继续对话微调 |
| 反向追问 | 信息缺失仍在 2.5 拦截；优化不替代必填校验 |

## Agent 检查清单

- [ ] 是否询问并提供 JD（可选）？
- [ ] 是否对 `analyze_star` 标记的单薄描述做了 STAR 扩写？
- [ ] 是否有 JD 时执行 `jd_match --apply --write`？
- [ ] 扩写是否避免编造技术与数据？
- [ ] 优化后是否 `validate_resume.py` 通过？
