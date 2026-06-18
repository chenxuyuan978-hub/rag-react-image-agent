# 系统设计文档

## 1. 项目背景

图像处理论文复现实验通常需要同时完成论文阅读、实验参数查找、图像处理、指标计算、结果整理和报告撰写。对于课程设计、科研入门或工程展示项目来说，常见问题包括：

- 实验设置分散在论文不同章节中。
- 方法参数和评价指标需要人工反复查找。
- 手动复现实验步骤多，容易遗漏中间结果。
- 不同算法的对比结果缺少统一管理。
- 实验结果和报告整理耗时，且可追溯性不足。

本项目尝试构建一个本地可运行的图像处理论文复现实验分析 Agent。它不是“自动复现任意论文”的系统，而是把论文检索、实验运行、指标分析、报告生成、历史归档和 Agent 工作流组织为一个可测试、可扩展的工程项目。

## 2. 总体架构

```text
用户 / Streamlit
        |
        v
FastAPI
        |
        v
规则 ReAct Agent / LangGraph Agent / Reproduction Intake
        |
        v
RAG 检索 -> LLM 抽取 -> 实验运行 -> 指标分析 -> 报告生成
真实论文/源码 -> Paper Loader / Source Ingestion -> Workspace + Summary
        |
        v
data/outputs / data/runs / data/reproduction_runs / reports / metrics
```

系统分为两条 Agent 路径：

- 规则 ReAct Agent：固定执行顺序，作为稳定 baseline。
- LangGraph Agent：第三阶段新增，用节点式工作流组织检索、抽取、实验、分析和报告生成。

第五阶段新增真实论文与源码接入路径：

```text
Streamlit
  -> FastAPI
  -> Reproduction Intake
  -> Paper Loader / Source Ingestion
  -> Workspace + Summary
```

它当前是独立接入能力，暂时不直接接入原有 LangGraph 实验 workflow。后续第六阶段会把 repo analysis 和 environment planning 接入新的 reproduction workflow。

## 3. 模块划分

### app/api

FastAPI 后端接口层。负责接收 HTTP 请求，调用已有业务模块，并返回结构化响应。

主要接口包括：

- 实验运行。
- 多算法对比实验。
- 规则 ReAct Agent。
- LangGraph Agent。
- 历史实验列表。
- 实验详情。
- 报告读取。
- 真实论文与源码接入。
- Reproduction runs 列表和 summary 读取。

### app/rag

本地 RAG 检索模块。当前支持读取 `.txt` 和 `.md` 文档，按固定长度切块，并使用 TF-IDF 检索相关论文片段。

### app/react

规则 ReAct Agent 和工具层。当前不接真实 LLM，使用固定流程调用：

- `RagRetrieveTool`
- `RunExperimentTool`
- `AnalyzeMetricsTool`
- `GenerateReportTool`

### app/graph

LangGraph Agent 工作流模块。用节点组织：

- 论文片段检索。
- LLM 实验配置抽取。
- 实验运行。
- 指标分析。
- 报告生成。
- 错误诊断。
- 一次性重试。

### app/llm

LLM 配置和客户端抽象层。当前默认使用 `FakeLLMClient`，不需要真实 API Key，也不会联网。它为后续接入真实 LLM provider 预留统一接口。

### app/experiments

实验运行模块。负责读取 YAML 配置，执行图像处理操作，保存输出图像、`metrics.csv` 和 `summary.json`。

同时包含多算法对比实验能力，支持生成 `comparison_metrics.csv`、`comparison_summary.json` 和指标对比图表。

### app/reports

报告与图表模块。负责生成 Markdown 实验报告和 MSE / PSNR / SSIM 对比图。

### app/evaluation

Agent Evaluation 模块。使用固定样例检查 LangGraph Agent 是否按预期执行节点、生成输出并处理错误。

### app/observability

可观测性配置模块。当前主要包含 LangSmith tracing 配置，默认关闭，缺少 API Key 时不会影响系统运行。

### app/paper

论文加载模块。负责从真实论文文件中提取文本，当前支持 txt、md 和可选 PDF 解析。PDF 解析优先使用 `pypdf`，其次尝试 `PyPDF2`；如果环境中没有 PDF 解析库，会返回清晰错误信息。

### app/repo

源码接入模块。负责接收源码 zip 或本地源码目录，将材料接入到 reproduction workspace 的 `source/` 目录，并统计源码文件数量和顶层结构。zip 解压时会检查路径，防止 zip slip 路径穿越。

### app/reproduction

真实论文与源码接入模块。负责创建 `data/reproduction_runs/{run_id}/` 独立 workspace，串联论文复制、论文解析、源码接入和 `intake_summary.json` 生成。

### frontend

Streamlit 前端。当前包含：

- 单次 Agent 实验。
- 历史实验。
- 多算法对比实验。
- 智能 Agent。
- 论文源码接入。
- 项目说明。

## 4. 规则 ReAct Agent 流程

规则 ReAct Agent 位于 `app/react`，作为稳定 baseline。它保留 Thought / Action / Observation / Final Answer 的执行轨迹，但流程是规则驱动的，不依赖 LLM 推理。

执行顺序：

```text
RagRetrieveTool
  -> RunExperimentTool
  -> AnalyzeMetricsTool
  -> GenerateReportTool
```

该流程适合验证基本工具链是否稳定，也方便前端和 API 在不依赖真实模型的情况下运行。

## 5. LangGraph Agent 流程

LangGraph Agent 位于 `app/graph`，使用 `StateGraph` 构建节点式工作流。

正常流程：

```text
retrieve_paper_context
  -> extract_experiment_spec
  -> run_experiment
  -> analyze_metrics
  -> generate_report
```

节点说明：

- `retrieve_paper_context`：从论文目录读取 txt/md 文档，切块并检索相关片段。
- `extract_experiment_spec`：调用 LLM 抽取 method、params、metrics。当前默认使用 FakeLLM。
- `run_experiment`：根据 YAML 配置运行实验。
- `analyze_metrics`：读取 `metrics.csv` 并生成简要指标分析。
- `generate_report`：生成 Markdown 报告。

当前版本仍使用 YAML 配置运行实验，尚未把 LLM 抽取结果自动转换成实验 YAML。

## 6. LangSmith 可观测性设计

LangSmith tracing 是可选能力，默认关闭。

配置项包括：

- `LANGSMITH_TRACING`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `LANGSMITH_ENDPOINT`

如果 `LANGSMITH_TRACING=true` 且提供了 API Key，系统会设置 LangSmith 环境变量。否则保持 tracing 关闭。无 Key 时，测试、前端、后端和 Docker 都应正常运行。

## 7. 错误诊断与重试机制

LangGraph 工作流支持结构化错误诊断。当前错误类型包括：

- `config_error`
- `file_not_found`
- `experiment_error`
- `metrics_error`
- `report_error`
- `unknown_error`

当 `run_experiment`、`analyze_metrics` 或 `generate_report` 失败时，workflow 进入 `diagnose_error` 节点，生成：

- 错误类型。
- 失败节点。
- 原始错误信息。
- 可能原因。
- 建议操作。
- 是否可重试。

当前默认最大重试次数为 1。本阶段只对常见的实验运行失败尝试重新进入 `run_experiment`，不会无限重试。

## 8. Agent Evaluation 设计

Agent Evaluation 位于 `app/evaluation`，用于评估 LangGraph Agent 的工作流级行为。

它与普通 pytest 不同：

- pytest 更关注函数、模块、边界条件和 API 合约。
- Agent Evaluation 更关注完整 Agent 工作流是否按预期完成任务。

当前检查内容包括：

- 是否执行预期节点。
- 是否生成预期输出。
- 错误场景是否进入 `diagnose_error`。
- 是否在无真实 LLM API Key、无 LangSmith API Key 条件下稳定运行。

默认评估样例：

- `gaussian_blur_success`
- `missing_config_error`
- `empty_paper_dir`

运行命令：

```bash
python scripts/run_agent_evaluation.py
```

## 9. 数据流

输入：

- 论文片段：来自 `data/papers` 或上传文件。
- 实验配置：YAML 文件，例如 `examples/demo_config.yaml`。
- 输入图像和参考图像：位于 `data/images` 或上传目录。

处理过程：

```text
论文片段 -> RAG 检索 -> LLM 抽取
实验配置 -> 实验运行 -> 输出图像
输出图像 + 参考图像 -> 指标计算
summary.json + metrics.csv + 论文片段 -> report.md
```

输出：

- 输出图像：例如 `step_01_gaussian_blur.png`。
- `metrics.csv`：记录 MSE、PSNR、SSIM。
- `summary.json`：记录实验名称、输出路径、配置摘要。
- `report.md`：Markdown 实验报告。
- `comparison_metrics.csv`：多算法对比指标。
- `comparison_summary.json`：多算法对比摘要。
- 指标对比图：MSE、PSNR、SSIM PNG 图表。
- `trace.txt`：部分 API/Agent 运行时保存的执行轨迹。

归档目录：

```text
data/runs/{run_id}/
```

### 真实论文与源码接入数据流

输入：

- 论文路径：txt、md 或 pdf。
- 源码路径：zip 或本地源码目录。

处理过程：

```text
paper_path + source_path
  -> POST /api/reproduction/intake
  -> run_reproduction_intake()
  -> 创建 data/reproduction_runs/{run_id}/
  -> 复制论文到 paper/
  -> 解析论文文本为 paper_text.txt
  -> 复制或解压源码到 source/
  -> 统计论文文本和源码文件
  -> 生成 intake_summary.json
```

输出：

- `data/reproduction_runs/{run_id}/paper/`
- `data/reproduction_runs/{run_id}/source/`
- `data/reproduction_runs/{run_id}/artifacts/`
- `data/reproduction_runs/{run_id}/logs/`
- `data/reproduction_runs/{run_id}/intake_summary.json`

当前第五阶段的 reproduction intake 是独立接入能力，暂时不直接接入原有 LangGraph Agent 主线。已有智能 Agent 主线仍然是：

```text
Streamlit
  -> FastAPI
  -> LangGraph Agent
  -> RAG / LLM / Experiment / Metrics / Report
```

## 10. 工程化设计

### pytest

覆盖图像处理、指标计算、配置读取、实验运行、RAG、ReAct 工具、LangGraph workflow、API、前端导入、Agent Evaluation 等模块。

### Ruff / Black

使用 Ruff 做静态检查和导入排序，使用 Black 统一代码格式。

### GitHub Actions

CI 在 push 或 pull request 到 `main` 分支时自动运行：

- 依赖安装。
- Black 检查。
- Ruff 检查。
- pytest。

### Docker

Dockerfile 使用 Python slim 镜像和 `opencv-python-headless`，减少 GUI 系统库依赖。

Docker Compose 启动两个服务：

- `backend`：FastAPI，端口 8000。
- `frontend`：Streamlit，端口 8501。

frontend 通过 `API_BASE_URL=http://backend:8000` 访问 backend，避免容器内 `localhost` 指向错误。

## 11. 当前限制

- 当前主要支持 demo 图像处理实验和传统图像处理算法。
- 第五阶段支持真实论文与源码接入，但不执行真实源码。
- PDF 解析依赖可选库 `pypdf` 或 `PyPDF2`。
- 当前 LLM 默认是 FakeLLM，不代表真实模型推理能力。
- 当前 LangGraph 工作流还没有自动把抽取结果写回 YAML。
- 当前不能保证自动复现任意真实论文。
- 当前不分析源码依赖、不自动构建环境、不自动生成 Dockerfile、不自动下载数据集或模型权重。
- 深度学习论文复现需要额外处理数据集、模型权重、CUDA、依赖版本、随机种子和评估协议。

## 12. 后续计划

- 支持 PDF 论文解析。
- 使用 embedding RAG 替换或增强 TF-IDF。
- 接入 FAISS / Chroma 向量数据库。
- 接入真实 LLM provider。
- 自动根据抽取结果生成实验 YAML。
- 管理真实论文代码仓库、依赖环境和运行脚本。
- 分析源码结构与环境规划。
- 在隔离容器中执行受控实验任务。
- 增强报告模板和可视化面板。
