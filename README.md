# 基于 RAG 与 ReAct 的图像处理论文复现实验分析 Agent

这是一个面向图像处理论文复现实验的本地实验平台。项目可以读取论文资料，检索实验设置，运行图像处理实验，计算评价指标，生成 Markdown 报告，并通过 FastAPI 与 Streamlit 提供后端接口和前端页面。

当前版本保持本地可运行：RAG 使用 TF-IDF，ReAct 使用规则驱动流程，不依赖 OpenAI API，不需要在线模型服务。

## 项目简介

图像处理论文复现实验通常需要手动查找方法参数、准备输入图像、运行实验、计算指标并整理报告。本项目把这些步骤拆成可测试的模块，并用 RAG + ReAct 的方式串联起来：

- RAG 从 `.txt` / `.md` 论文资料中检索实验设置；
- ReAct Agent 按固定步骤调用检索、实验、指标分析和报告生成工具；
- 实验运行器根据 YAML 配置执行图像处理操作；
- 平台记录每次实验的 `run_id`，便于回溯历史结果；
- Streamlit 前端支持单次 Agent 实验、历史实验查看和多算法对比。

## 核心功能

- 论文资料读取：支持 `.txt` 和 `.md`；
- 本地 RAG 检索：使用 scikit-learn `TfidfVectorizer`；
- 规则驱动 ReAct Agent：保留 Thought / Action / Observation / Final Answer 轨迹；
- 图像处理实验：支持 `gaussian_blur`、`median_blur`、`sharpen`、`edge_detect`、`histogram_equalization`；
- 图像指标计算：支持 MSE、PSNR、SSIM；
- Markdown 报告生成：输出实验配置摘要、流程、指标和论文片段；
- FastAPI 后端：提供健康检查、实验运行、Agent 运行、历史查询等接口；
- Streamlit 前端：支持文件上传、历史实验、实验详情和多算法对比展示；
- run_id 实验归档：每次运行保存到独立目录；
- 多算法对比实验：批量运行多个方法并生成指标表和对比图；
- 工程化能力：pytest、Black、Ruff、GitHub Actions、Docker Compose。

## 系统架构

```text
用户任务 / YAML 配置
        |
        v
论文资料加载 -> RAG 检索 -> ReAct 工具调用
        |                         |
        |                         v
        |                  图像处理实验运行
        |                         |
        |                         v
        |                  指标计算与图表生成
        |                         |
        v                         v
     论文片段  ------------>  Markdown 报告
                                  |
                                  v
                         run_id 历史归档 / 前端展示
```

主要模块：

- `app/rag`：论文加载、文本切块和 TF-IDF 检索；
- `app/react`：规则驱动 Agent、工具层和 trace；
- `app/image_ops`：图像读取、处理函数和评价指标；
- `app/experiments`：实验配置、单次实验运行、多算法对比实验；
- `app/reports`：Markdown 报告和指标对比图表；
- `app/core`：run_id 归档、历史列表和实验详情；
- `app/api`：FastAPI 后端；
- `frontend`：Streamlit 前端。

## 快速开始

进入项目目录：

```bash
cd rag_react_image_agent
```

创建并激活虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

运行测试：

```bash
python -m pytest
```

## 本地运行

生成 demo 图像数据：

```bash
python scripts/prepare_demo_data.py
```

运行普通图像处理实验：

```bash
python scripts/run_demo_experiment.py examples/demo_config.yaml
```

运行 RAG 检索 demo：

```bash
python scripts/run_rag_demo.py
```

运行完整 ReAct demo：

```bash
python scripts/run_react_demo.py
```

运行多算法对比实验：

```bash
python scripts/run_comparison_experiment.py examples/comparison_config.yaml
```

## Docker 运行

使用 Docker Compose 同时启动后端和前端：

```bash
docker compose up --build
```

访问地址：

- FastAPI 文档：`http://localhost:8000/docs`
- Streamlit 前端：`http://localhost:8501`

Docker 镜像使用 `opencv-python-headless`，减少对系统 GUI 库的依赖，更适合服务器和 CI 环境。

## FastAPI 接口

启动后端：

```bash
python -m uvicorn app.api.main:app --reload
```

常用接口：

- `GET /health`：健康检查；
- `POST /api/experiments/run`：根据 YAML 运行单次实验；
- `POST /api/experiments/compare`：运行多算法对比实验；
- `POST /api/agent/run`：运行规则驱动 ReAct Agent；
- `GET /api/runs`：获取历史实验列表；
- `GET /api/runs/{run_id}`：获取某次实验摘要；
- `GET /api/runs/{run_id}/detail`：获取某次实验详情；
- `GET /api/reports/{report_name}`：读取 `data/outputs` 下的报告文本。

接口文档：

```text
http://127.0.0.1:8000/docs
```

## Streamlit 前端

启动前端：

```bash
streamlit run frontend/streamlit_app.py
```

前端包含四个页面：

- 单次 Agent 实验：上传论文、输入图像和参考图像，运行 ReAct 流程；
- 历史实验：查看 `data/runs` 下的 run 列表，并查看 summary、metrics、report、trace 和输出图像；
- 多算法对比实验：使用 `examples/comparison_config.yaml` 或上传 YAML 运行对比实验；
- 项目说明：展示项目当前能力和用途。

## LLM 配置

第三阶段会逐步接入 LangGraph、LangSmith 和真实 LLM。当前版本先提供统一的 LLM 配置与客户端适配层，默认使用 `FakeLLMClient`，不需要真实 API Key，也不会联网调用模型。

示例环境变量见 `.env.example`：

```env
LLM_PROVIDER=fake
LLM_MODEL=fake-local
LLM_API_KEY=
LLM_BASE_URL=
LLM_TEMPERATURE=0.0
LLM_TIMEOUT_SECONDS=60
```

预留 LangSmith 配置：

```env
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=rag-react-image-agent
```

当前默认 FakeLLM 的好处是：本地开发、CI、Docker 都可以在没有密钥的情况下稳定运行。后续接入真实 LLM 时，可以在不改动现有实验、RAG、报告模块的前提下替换客户端实现。

## LLM 实验配置抽取

当前 LLM 层已经支持从论文片段中抽取实验配置，输出统一的 `ExperimentSpec`：

- `method`：项目内部方法名，例如 `gaussian_blur`；
- `params`：方法参数，例如 `{"kernel_size": 5}`；
- `metrics`：评价指标，例如 `["mse", "psnr", "ssim"]`；
- `raw_response`：LLM 原始响应，方便调试。

运行 demo：

```bash
python scripts/run_llm_extraction_demo.py
```

当前默认仍使用 `FakeLLMClient`，不需要真实 API Key。FakeLLM 会返回稳定 JSON，方便本地开发和 CI 测试。后续第三阶段会接入 LangGraph 工作流，把抽取结果用于自动生成实验配置，并进一步接入 LangSmith 进行链路追踪。

## LangGraph 工作流

项目现在同时保留两套 Agent 组织方式：

- 旧版规则 ReAct Agent：位于 `app/react/agent.py`，流程固定、稳定可测，继续作为已有 API 和前端能力的基础；
- 新增 LangGraph Agent：位于 `app/graph/`，用节点式工作流组织论文检索、LLM 实验配置抽取、实验运行、指标分析和报告生成。

当前 LangGraph 工作流节点顺序：

```text
retrieve_paper_context
  -> extract_experiment_spec
  -> run_experiment
  -> analyze_metrics
  -> generate_report
```

运行 demo：

```bash
python scripts/run_langgraph_demo.py
```

本阶段仍默认使用 `FakeLLMClient`，不需要真实 LLM API Key，也不启用 LangSmith。后续可以把 LangGraph 节点接入真实 LLM、LangSmith tracing 和自动 YAML 配置生成。

## LangSmith Trace 可观测性

LangSmith tracing 是可选能力，默认不开启。本地开发、Docker 和 CI 都不依赖 LangSmith，也不需要 LangSmith API Key。

如需在 LangSmith 平台查看 LangGraph 工作流 trace，可以设置环境变量：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=你的 LangSmith API Key
LANGSMITH_PROJECT=rag-react-image-agent
```

然后运行：

```bash
python scripts/run_langgraph_demo.py
```

如果 `LANGSMITH_TRACING=true` 但没有提供 `LANGSMITH_API_KEY`，项目会自动保持 tracing 关闭，不会影响测试、前端、后端或 Docker 启动。

## 多算法对比实验

对比实验配置示例：

```yaml
comparison_name: demo_denoising_comparison
input_image: data/images/input.png
reference_image: data/images/reference.png
methods:
  - name: gaussian_blur
    params:
      kernel_size: 5
  - name: median_blur
    params:
      kernel_size: 5
  - name: sharpen
    params: {}
metrics:
  - mse
  - psnr
  - ssim
output_dir: data/outputs/demo_denoising_comparison
```

运行后会生成：

- 每个算法的输出图像；
- `comparison_metrics.csv`；
- `comparison_summary.json`；
- `mse_comparison.png`；
- `psnr_comparison.png`；
- `ssim_comparison.png`。

## 历史实验管理

FastAPI 和部分脚本会为实验创建独立 `run_id`，结果保存到：

```text
data/runs/{run_id}/
```

历史实验支持：

- 列出所有 run；
- 查看某次 run 的 summary；
- 查看 metrics 表格；
- 查看 Markdown 报告；
- 查看 trace；
- 查看输出图像；
- 查看对比实验图表。

`data/runs`、`data/outputs` 和 `data/indexes` 默认只保留 `.gitkeep`，真实运行结果不会作为核心代码提交。

## 测试与 CI

本地测试：

```bash
python -m pytest
```

代码格式检查：

```bash
python -m black --check app tests scripts frontend
python -m ruff check app tests scripts frontend
```

项目已配置 GitHub Actions。每次 push 或 pull request 到 `main` 分支时，CI 会自动执行依赖安装、Black、Ruff 和 pytest。

## 项目截图位置提示

后续可以在以下目录补充截图：

```text
docs/assets/
```

建议截图包括：

- Streamlit 单次 Agent 实验页面；
- 历史实验列表页面；
- run detail 展示页面；
- 多算法对比实验页面；
- FastAPI Swagger 文档页面。

## 后续可扩展方向

- PDF 论文解析；
- embedding RAG；
- FAISS / Chroma 向量数据库；
- 接入 LLM 做实验设置抽取和动态工具选择；
- 深度学习图像复现模型；
- 更完整的实验参数管理和报告模板。
