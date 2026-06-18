# 真实论文与源码接入说明

本文档说明第五阶段新增的真实论文与源码接入能力。它的目标是把系统从 demo 论文和 demo 配置，升级为可以接收真实论文文件和源码材料的复现任务入口。

## 1. 阶段目标

第五阶段的目标是建立真实复现任务的输入层：

- 接收真实论文文件；
- 接收真实源码目录或源码 zip；
- 为每次复现任务创建独立 workspace；
- 保存论文文本、源码材料和接入摘要；
- 为后续源码分析、环境规划和容器化执行提供基础。

本阶段不执行真实源码，不安装依赖，不构建论文运行环境，也不保证自动复现任意论文。

## 2. 支持的输入

论文文件支持：

- `.txt`
- `.md`
- `.pdf`

源码材料支持：

- 本地源码目录；
- 源码 `.zip` 文件。

PDF 解析是可选能力。如果环境中安装了 `pypdf`，系统会优先使用它；如果没有 `pypdf` 但安装了 `PyPDF2`，则尝试使用 `PyPDF2`。如果两个库都不存在，处理 PDF 时会返回清晰错误提示，项目测试和 CI 不依赖 PDF 解析库。

## 3. Workspace 结构

默认根目录：

```text
data/reproduction_runs/
```

每次任务会创建独立目录：

```text
data/reproduction_runs/{run_id}/
├── paper/
├── source/
├── artifacts/
├── logs/
└── intake_summary.json
```

目录用途：

- `paper/`：保存原始论文文件和解析后的 `paper_text.txt`。
- `source/`：保存复制后的源码目录或解压后的 zip 内容。
- `artifacts/`：预留给后续复现实验产物，例如中间结果、图表和报告。
- `logs/`：预留给后续源码分析、环境规划和执行日志。
- `intake_summary.json`：保存本次接入任务摘要。

## 4. 输出文件

### paper_text.txt

`paper_text.txt` 保存从论文中提取出的纯文本。对于 txt/md 文件，系统直接读取文本；对于 PDF 文件，系统尝试使用可选 PDF 解析库提取文本。

### intake_summary.json

`intake_summary.json` 使用 UTF-8 保存，记录本次接入任务的关键字段：

- `run_id`
- `workspace_dir`
- `paper_input_path`
- `source_input_path`
- `paper_saved_path`
- `source_saved_path`
- `paper_text_path`
- `paper_text_chars`
- `paper_text_lines`
- `source_file_count`
- `source_top_level_items`
- `status`
- `warnings`
- `errors`

## 5. FastAPI 接口

### POST /api/reproduction/intake

功能：创建真实论文与源码接入任务。

请求示例：

```json
{
  "paper_path": "data/sample_inputs/papers/demo_paper.txt",
  "source_path": "data/sample_inputs/repos/demo_repo"
}
```

返回字段说明：

- `run_id`：本次复现接入任务 ID。
- `workspace_dir`：任务 workspace 路径。
- `paper_saved_path`：论文复制后的路径。
- `source_saved_path`：源码复制或解压后的路径。
- `paper_text_path`：论文文本保存路径。
- `paper_text_chars` / `paper_text_lines`：论文文本字符数和行数。
- `source_file_count`：源码文件数量。
- `source_top_level_items`：源码顶层目录或文件列表。
- `status`：任务状态，例如 `completed` 或 `failed`。
- `warnings` / `errors`：警告和错误信息。

### GET /api/reproduction/runs

功能：列出 `data/reproduction_runs` 下已有的复现接入任务。

请求示例：

```http
GET /api/reproduction/runs
```

返回字段包括：

- `run_id`
- `status`
- `workspace_dir`
- `paper_text_chars`
- `source_file_count`
- `created_at`

### GET /api/reproduction/runs/{run_id}

功能：读取指定复现接入任务的 `intake_summary.json`。

请求示例：

```http
GET /api/reproduction/runs/repro_20260618_153000
```

如果 `run_id` 不存在，或者对应目录下没有 `intake_summary.json`，接口会返回清晰 HTTP 错误。

## 6. Streamlit 使用方式

前端新增 Tab：

```text
论文源码接入
```

使用方式：

1. 启动 FastAPI 后端。
2. 启动 Streamlit 前端。
3. 进入 `论文源码接入` 页面。
4. 输入 `paper_path` 和 `source_path`。
5. 点击创建复现任务。

页面会展示：

- `run_id`
- `workspace_dir`
- 论文文本字符数和行数；
- 源码文件数量；
- 源码顶层结构；
- `warnings` 和 `errors`；
- 完整 `intake_summary` JSON；
- 历史 reproduction runs 列表。

启动命令：

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
python -m streamlit run frontend/streamlit_app.py
```

## 7. 安全与边界

当前阶段做了以下边界控制：

- zip 解压时检查路径，防止 zip slip 路径穿越。
- 不执行用户上传或指定的源码。
- 不安装源码依赖。
- 不自动生成 Dockerfile。
- 不自动下载数据集或模型权重。
- 不对真实论文指标做自动对齐。
- `data/reproduction_runs/` 不应提交到 Git。

这些约束是有意保留的：真实源码执行需要容器隔离、资源限制、超时控制、日志捕获和命令白名单，属于后续阶段。

## 8. 后续计划

第六阶段会在当前 workspace 基础上做源码结构分析与环境规划，例如：

- 识别 `requirements.txt`、`environment.yml`、`pyproject.toml` 等依赖文件；
- 分析 README 中的运行命令；
- 识别可能的入口脚本、配置文件和数据目录；
- 生成环境规划摘要；
- 为第七阶段容器化执行做准备。
