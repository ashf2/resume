# 头像插入指南

简历页眉右侧圆形头像，由 `avatar` 字段控制。

## Agent 强制规则

- **每次生成简历都必须询问用户**是否要头像，不得跳过。
- **禁止**未经询问沿用 `output/resume.json` 里旧头像配置。
- **禁止**在未询问时默认 `hidden: true` 并直接渲染。
- 须在用户明确选择后，于 **finalize 之后** 对 `output/resume.json` 执行 `setup_avatar.py`。

## 向用户收集头像（必问话术）

整合完内容、展示摘要后，**与主题选择一同发送**：

> 是否需要添加头像照片？
>
> 1. **上传图片**：在对话中发送照片，或提供电脑上的图片路径（如 `D:\photo.jpg`）
> 2. **提供图片链接**：公网可访问的 URL（如 GitHub 头像）
> 3. **暂不需要**：简历不显示头像区域
>
> 请回复 1 / 2 / 3，或直接发送图片。

用户未答复前，不得定稿渲染。

## JSON 字段

```json
"avatar": {
  "src": "avatars/蒋东海.jpg",
  "hidden": false
}
```

| `src` 类型 | 示例 | 说明 |
|------------|------|------|
| 相对路径 | `avatars/photo.jpg` | 推荐：图片在 `output/avatars/` |
| 网络 URL | `https://...` | 外链头像 |
| Base64 | `data:image/jpeg;base64,...` | 单文件 HTML |
| 隐藏 | `hidden: true` | 用户选择「不需要」时设置 |

draft 阶段可保持 `hidden: true` 占位；最终状态由用户选择决定。

## Agent 处理步骤（定稿后）

### 用户上传或本地路径

```bash
python skills/resume-generator/scripts/setup_avatar.py "用户提供的图片路径" -r output/resume.json
```

### 用户提供 URL

```bash
python skills/resume-generator/scripts/setup_avatar.py "https://..." -r output/resume.json
```

### 用户不要头像

```bash
python skills/resume-generator/scripts/setup_avatar.py --hide -r output/resume.json
```

### 单文件 HTML（图片内嵌）

```bash
python skills/resume-generator/scripts/setup_avatar.py "路径或URL" -r output/resume.json --embed
python skills/resume-generator/scripts/render_resume.py output/resume.json --embed-avatar
```

## 图片要求

- 格式：JPG、PNG、WebP、GIF
- 建议：正方形或近正方形，≥ 200×200 像素，正面清晰
