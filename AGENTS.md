# AGENTS.md

> 本文件为 Agent（AI 编程助手）协作规范，所有 Agent 操作本仓库时必须严格遵守。

---

## 📌 仓库定位

`agent-learning` 是 Agent 工程学习仓库，内容以概念整理、知识梳理为主，后续逐步补充代码示例和实践案例。

---

## 🚫 核心禁令：禁止直接 Push 到 Main 分支

**任何改动禁止直接提交或推送到 `main` 分支。**

所有变更必须遵循 **Feature Branch Workflow**：

```
main 分支（受保护）
    ↑
    │  Pull Request（合并请求）
    │
feature/xxx 分支（本地开发 + 远程推送）
```

### 标准操作流程

```bash
# 1. 确保本地 main 最新
git checkout main
git pull origin main

# 2. 从 main 切出功能分支
# 命名规范：feature/<简短描述> 或 docs/<简短描述>
git checkout -b feature/add-xxx

# 3. 修改文件、本地验证

# 3.5 代码格式化（如包含 Python 文件）
ruff format .
ruff check --fix .

# 4. 提交（遵循 Commit Message 规范）
git add <文件>
git commit -m "type: 描述"

# 5. 推送到远程同名分支
git push -u origin feature/add-xxx

# 6. 在 GitHub 上发起 Pull Request，目标分支为 main
# 7. 合并后，本地清理分支
```

---

## 📝 分支命名规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能、新增内容 | `feature/add-react-agent` |
| `docs/` | 文档修改、补充 | `docs/update-rag-section` |
| `fix/` | 错误修正 | `fix/typo-in-memory` |
| `refactor/` | 重构（不改变功能） | `refactor/restructure-toc` |

---

## ✍️ Commit Message 规范

格式：`type: 描述`

| type | 含义 |
|------|------|
| `feat` | 新功能、新章节 |
| `docs` | 文档修改 |
| `fix` | 修复错误 |
| `refactor` | 重构 |
| `style` | 格式调整（无内容变更） |
| `chore` | 杂项（配置、依赖等） |

**示例：**
- `docs: 补充 ReAct 框架架构图`
- `feat: 新增 Multi-Agent 协作模式章节`
- `fix: 修正 Memory 章节中的笔误`

---

## 🤖 Agent 协作守则

1. **改前确认**：修改现有内容前，向用户确认范围和意图。
2. **独立实现**：新功能尽量独立实现，不擅自改动已有代码/文档结构。
3. **中文优先**：所有文档、注释、Commit Message 使用中文。
4. **最小变更**：每次 PR 聚焦单一目标，避免大杂烩式提交。
5. **绝不直推 main**：无论多小的改动，都必须走分支 + PR 流程。
6. **提交前格式化**：涉及 Python 代码的变更，提交前必须执行 `ruff format .` 和 `ruff check --fix .`，确保代码风格统一。

---

## 🔒 分支保护建议（仓库管理员配置）

GitHub 仓库设置路径：**Settings → Branches → Add rule**

| 配置项 | 建议 |
|--------|------|
| Branch name pattern | `main` |
| Require a pull request before merging | ✅ 勾选 |
| Require approvals | 至少 1 人（单人维护时可设为 0） |

> 本规范自文件创建之日起生效，适用于所有后续变更。
