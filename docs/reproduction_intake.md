# Real Paper And Source Intake

本文档说明第五阶段第 5.2 步新增的真实论文与源码接入能力。

## 阶段目标

第五阶段的目标是让系统从 demo 论文和 demo 配置，逐步升级为可以接收真实论文文件和真实源码材料的复现任务入口。

当前第 5.2 步只负责后端 API 与前端入口：

- 接收论文文件路径和源码路径；
- 调用已有 intake 核心模块；
- 为每次任务创建独立 workspace；
- 保存 `intake_summary.json`；
- 在 Streamlit 中展示创建结果和历史复现任务。

本阶段不执行真实论文源码，不自动安装依赖，也不构建论文运行环境。

## 支持输入

论文文件支持：

- `.pdf`
- `.md`
- `.txt`

源码材料支持：

- 本地源码目录；
- 源码 `.zip` 文件。

PDF 解析是可选能力：如果环境中安装了 `pypdf` 或 `PyPDF2`，系统会尝试解析；如果没有 PDF 解析库，系统会返回清晰错误提示。

## Workspace 结构

默认复现任务根目录：

```text
data/reproduction_runs/
```

每次任务会创建独立目录，例如：

```text
data/reproduction_runs/repro_20260618_153000/
├── paper/
├── source/
├── artifacts/
├── logs/
└── intake_summary.json
```

其中：

- `paper/` 保存输入论文文件和解析后的 `paper_text.txt`；
- `source/` 保存源码目录或解压后的 zip 内容；
- `artifacts/` 预留给后续复现实验产物；
- `logs/` 预留给后续环境检查和源码执行日志；
- `intake_summary.json` 保存本次接入任务摘要。

## FastAPI 接口

### 创建复现接入任务

```http
POST /api/reproduction/intake
```

请求体：

```json
{
  "paper_path": "data/sample_inputs/papers/demo_paper.txt",
  "source_path": "data/sample_inputs/repos/demo_repo"
}
```

返回内容包含：

- `run_id`
- `workspace_dir`
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

### 获取复现任务列表

```http
GET /api/reproduction/runs
```

返回 `data/reproduction_runs` 下已有任务的摘要列表。

### 获取单个复现任务详情

```http
GET /api/reproduction/runs/{run_id}
```

读取指定任务目录下的 `intake_summary.json`。如果任务不存在或 summary 缺失，会返回清晰的 HTTP 错误。

## Streamlit 页面

前端新增 Tab：

```text
论文源码接入
```

页面支持：

- 输入论文文件路径；
- 输入源码路径；
- 输入 FastAPI 服务地址；
- 创建复现任务；
- 查看返回的 `intake_summary`；
- 刷新历史复现任务列表。

启动方式：

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
python -m streamlit run frontend/streamlit_app.py
```

或使用 Docker：

```bash
docker compose up --build
```

## 当前不支持

为了避免夸大能力，当前阶段明确不做以下事情：

- 不分析源码依赖；
- 不自动创建 Conda 或 Python 环境；
- 不安装论文源码依赖；
- 不执行真实论文源码；
- 不生成论文专用 Dockerfile；
- 不自动对齐真实论文的数据集和评估协议；
- 不保证自动复现任意真实论文。

## 后续第六阶段计划

第六阶段可以在当前 workspace 基础上继续增强：

- 扫描源码依赖文件，例如 `requirements.txt`、`environment.yml`、`pyproject.toml`；
- 生成环境分析报告；
- 识别 README 中的运行命令；
- 做源码入口文件和配置文件分析；
- 为后续半自动环境构建和实验执行做准备。
