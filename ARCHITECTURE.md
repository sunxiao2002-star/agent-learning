# 架构文档

> 本文件描述 `agent-learning` 仓库的模块结构、职责划分与核心设计决策。
> **每次提交前必须更新**，确保文档与代码保持一致。

---

## 目录结构

```
agent-learning/
├── main.py                    # 项目统一入口
├── AGENTS.md                  # Agent 协作规范（对 Assistant 强制约束）
├── ARCHITECTURE.md            # 本文档
├── Makefile                   # 开发命令封装（format / lint / install）
├── pyproject.toml             # 项目元数据 + Ruff 配置
├── requirements.txt           # 生产依赖
├── requirements-dev.txt       # 开发依赖
│
├── agents/                    # Agent 管理包
│   ├── __init__.py            # Agent 抽象基类 + AgentRegistry
│   └── deepseek/              # DeepSeek Agent 实现
│       ├── __init__.py        # 导出 DeepSeekAgent / DeepSeekClient / ChatConfig
│       ├── agent.py           # DeepSeekAgent（继承 Agent 基类，run() 收口）
│       ├── client.py          # DeepSeekClient（底层 API 封装）
│       ├── cli.py             # 交互式命令行工具
│       └── demo.py            # 基础调用示例
│
├── skills/                    # Skill 管理包
│   ├── __init__.py            # Skill 抽象基类 + SkillRegistry
│   └── md_to_html/            # Markdown 转 HTML Skill
│       ├── SKILL.md           # Skill 使用文档
│       ├── __init__.py        # 导出 MdToHtmlSkill
│       ├── skill.py           # MdToHtmlSkill（继承 Skill 基类，run() 收口）
│       ├── scripts/
│       │   └── convert.py     # 核心转换逻辑
│       └── assets/styles/     # 预设 CSS 主题
│           ├── minimal.css
│           ├── academic.css
│           ├── business.css
│           ├── dark.css
│           ├── elegant.css
│           └── magazine.css
│
├── logs/
│   └── commits/               # 提交日志（每次提交后自动/手动写入）
│
└── .vscode/
    └── settings.json          # VS Code 配置（Ruff 默认 formatter）
```

---

## 核心模块职责

### `agents/` — Agent 管理包

| 文件 | 职责 |
|------|------|
| `__init__.py` | 定义 `Agent` 抽象基类（`name` + `run()`）和 `AgentRegistry`（统一注册、发现、执行） |
| `deepseek/agent.py` | `DeepSeekAgent`：封装 `DeepSeekClient`，对外暴露 `run()` / `run_stream()` / `run_with_history()` / `reset()` 等统一接口 |
| `deepseek/client.py` | `DeepSeekClient`：底层 OpenAI 兼容客户端，处理认证、请求、重试、流式输出、历史持久化 |
| `deepseek/cli.py` | 交互式命令行入口，支持 `/quit`、`/reset`、`/save`、`/load`、`/history`、`/stream` 等快捷命令 |
| `deepseek/demo.py` | 最小可运行示例，演示单次流式对话 |

**设计决策**：
- `Agent` 与 `Client` 分层：`Agent` 负责业务语义（run 接口），`Client` 负责网络通信细节。
- 流式输出默认开启（`ChatConfig.stream = True`），CLI 直接走 `chat_with_history_stream`。
- API Key 统一从环境变量 `DEEPSEEK_API_KEY` 读取，不硬编码。

### `skills/` — Skill 管理包

| 文件 | 职责 |
|------|------|
| `__init__.py` | 定义 `Skill` 抽象基类（`name` + `description` + `run()`）和 `SkillRegistry` |
| `md_to_html/skill.py` | `MdToHtmlSkill`：封装 `convert`，暴露 `run(md_text)` 和 `run_file(input_path)` |
| `md_to_html/scripts/convert.py` | 核心转换逻辑，依赖 `markdown` 库 |
| `md_to_html/assets/styles/` | 6 套预设 CSS 主题 |

**设计决策**：
- Skill 与具体实现解耦：`Skill` 只定义接口，`scripts/convert.py` 负责具体逻辑。
- CSS 资源与代码同目录，通过 `Path(__file__).parent.parent` 相对定位，保证迁移后路径仍然正确。

### `main.py` — 项目统一入口

- 默认启动 `deepseek` Agent 的交互式 CLI。
- 预留 `--agent` / `--skill` 参数，支持未来扩展其他 Agent/Skill。
- 自动将项目根目录加入 `sys.path`，解决包导入问题。

---

## 依赖关系

```
main.py
  └─ agents.deepseek.cli
        └─ agents.deepseek.client
              └─ openai (第三方)

agents.deepseek.agent
  └─ agents (Agent 基类)
  └─ agents.deepseek.client

skills.md_to_html.skill
  └─ skills (Skill 基类)
  └─ skills.md_to_html.scripts.convert
        └─ markdown (第三方)
```

---

## 运行方式

```bash
# 默认启动 DeepSeek CLI
python3 main.py

# 显式指定 Agent
python3 main.py --agent deepseek

# 作为模块运行（等效）
python3 -m agents.deepseek.cli
python3 -m agents.deepseek.demo
```

---

## 更新记录

| 日期 | Commit | 变更摘要 |
|------|--------|----------|
| 2026-04-26 | 57caa29 | 重构 Skill/Agent 架构，添加基类、注册表和入口文件；stream 默认开启；加入 markdown 依赖 |
