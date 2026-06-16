# 基于 RAG + ReAct / LangGraph 的图像处理论文复现实验分析 Agent

本项目面向图像处理论文复现实验分析场景，目标是辅助用户从论文片段中检索实验设置，运行本地图像处理实验，计算评价指标，生成实验报告，并通过前端和 API 查看实验结果。

项目结合了本地 RAG 检索、规则 ReAct 工具链、LangGraph 工作流、LLM 实验配置抽取、Streamlit 可视化、FastAPI 后端和 Docker 部署能力。当前定位是“辅助论文复现实验分析”，不是“完全自动复现任意论文”。

## 核心功能

- 本地论文片段检索：支持 `.txt` 和 `.md`，使用 TF-IDF 检索。
- 图像处理实验运行：支持 `gaussian_blur`、`median_blur`、`sharpen`、`edge_detect`、`histogram_equalization`。
- 指标计算：支持 MSE、PSNR、SSIM。
- Markdown 实验报告生成：输出实验配置、处理流程、指标结果和论文相关片段。
- 规则 ReAct Agent：保留稳定 baseline，按固定工具链执行 RAG、实验、指标分析和报告生成。
- 实验历史管理：使用 `run_id` 归档实验结果，支持历史列表和实验详情读取。
- 多算法对比实验：对同一输入图像批量运行多个方法，生成指标表和对比图。
- LLM 配置抽象层：统一管理 provider、model、api_key、base_url、temperature 等配置。
- FakeLLM 测试模式：默认离线运行，不需要真实 LLM API Key。
- 论文实验配置抽取：从论文片段中抽取 method、params、metrics。
- LangGraph Agent 工作流：用节点式流程组织论文检索、LLM 抽取、实验运行、指标分析和报告生成。
- 可选 LangSmith tracing：默认关闭，有 Key 时可开启链路追踪。
- 失败诊断与一次性重试：对配置错误、文件缺失、实验错误、指标错误、报告错误进行分类诊断。
- Agent Evaluation：用固定样例评估 Agent 工作流的节点执行、输出完整性和错误处理能力。
- Streamlit 智能 Agent 页面：通过前端调用 LangGraph Agent API 并展示 steps、diagnosis、report_path 等结果。
- FastAPI 接口：提供实验运行、Agent 运行、历史实验、报告读取等 HTTP API。
- Docker / Docker Compose：支持后端和前端容器化启动。
- GitHub Actions CI：自动运行测试和代码质量检查。

## 系统架构

```text
用户 / Streamlit
        |
        v
FastAPI
        |
        v
规则 ReAct Agent / LangGraph Agent
        |
        v
RAG 检索 -> LLM 抽取 -> 实验运行 -> 指标分析 -> 报告生成
        |
        v
outputs / reports / metrics / run history
```

说明：

- 规则 ReAct Agent 是稳定 baseline，适合作为可解释、可测试的基础流程。
- LangGraph Agent 是第三阶段新增的智能工作流，用节点组织检索、抽取、实验、分析和报告生成。
- LangSmith 是可选观测能力，默认关闭，不影响本地运行、测试和 CI。
- Agent Evaluation 是工作流级评估能力，用于检查节点执行、输出完整性和错误处理。

## 快速开始

进入项目目录：

```bash
cd rag_react_image_agent
```

创建虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell 激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux 激活：

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

启动 FastAPI 后端：

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

启动 Streamlit 前端：

```bash
python -m streamlit run frontend/streamlit_app.py
```

Docker 启动：

```bash
docker compose up --build
```

访问地址：

- FastAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Streamlit: [http://localhost:8501](http://localhost:8501/)

## 常用脚本

生成 demo 图像数据：

```bash
python scripts/prepare_demo_data.py
```

运行基础实验：

```bash
python scripts/run_demo_experiment.py examples/demo_config.yaml
```

运行 RAG demo：

```bash
python scripts/run_rag_demo.py
```

运行规则 ReAct demo：

```bash
python scripts/run_react_demo.py
```

运行 LangGraph demo：

```bash
python scripts/run_langgraph_demo.py
```

运行 LLM 实验配置抽取 demo：

```bash
python scripts/run_llm_extraction_demo.py
```

运行 Agent Evaluation：

```bash
python scripts/run_agent_evaluation.py
```

运行多算法对比实验：

```bash
python scripts/run_comparison_experiment.py examples/comparison_config.yaml
```

## FastAPI 接口

常用接口：

- `GET /health`：健康检查。
- `POST /api/experiments/run`：根据 YAML 运行单次实验。
- `POST /api/experiments/compare`：运行多算法对比实验。
- `POST /api/agent/run`：运行规则驱动 ReAct Agent。
- `POST /api/agent/langgraph/run`：运行 LangGraph 智能 Agent 工作流。
- `GET /api/runs`：获取历史实验列表。
- `GET /api/runs/{run_id}`：获取某次实验摘要。
- `GET /api/runs/{run_id}/detail`：获取某次实验详情。
- `GET /api/reports/{report_name}`：读取 `data/outputs` 下的报告文本。

## Streamlit 前端页面

当前前端包含五个页面：

- 单次 Agent 实验：上传论文和图像，运行规则 ReAct 流程。
- 历史实验：查看 `data/runs` 下的历史 run，并展示 summary、metrics、report、trace 和输出图像。
- 多算法对比实验：运行 comparison YAML，展示指标表、对比图表和输出图像。
- 智能 Agent：调用 `POST /api/agent/langgraph/run`，展示 final_answer、report_path、steps、diagnosis、retry_count、extracted_spec 和 metrics_analysis。
- 项目说明：展示项目当前能力和用途。

本地直接启动前端时，默认调用 `http://localhost:8000`。Docker Compose 启动时，frontend 服务会使用 `API_BASE_URL=http://backend:8000` 访问后端容器。

## LLM 配置

当前默认使用 `FakeLLMClient`：

- 不需要真实 LLM API Key。
- 不联网调用模型。
- 返回稳定结果，便于本地开发、测试和 CI。

示例环境变量见 `.env.example`：

```env
LLM_PROVIDER=fake
LLM_MODEL=fake-local
LLM_API_KEY=
LLM_BASE_URL=
LLM_TEMPERATURE=0.0
LLM_TIMEOUT_SECONDS=60
```

后续可以通过环境变量扩展真实模型 provider，但当前测试和 CI 不依赖真实 LLM。

## LangSmith 配置

LangSmith tracing 默认关闭，本地运行、Docker 和 CI 都不依赖 LangSmith API Key。

如需开启：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=你的 Key
LANGSMITH_PROJECT=rag-react-image-agent
```

如果设置了 `LANGSMITH_TRACING=true` 但没有提供 `LANGSMITH_API_KEY`，项目会自动保持 tracing 关闭，不影响正常运行。

## Agent Evaluation

Agent Evaluation 用固定样例检查 LangGraph Agent 工作流是否按预期执行。

当前默认样例包括：

- `gaussian_blur_success`：正常 Gaussian Blur 实验流程。
- `missing_config_error`：缺失配置路径，验证错误诊断。
- `empty_paper_dir`：空论文目录，验证基础流程稳定性。

运行：

```bash
python scripts/run_agent_evaluation.py
```

输出包括每个 case 的通过状态、缺失节点、缺失输出、错误类型、报告路径，以及总计 `total`、`passed`、`failed`、`pass_rate`。

## 测试与代码质量

运行测试：

```bash
python -m pytest
```

代码格式和静态检查：

```bash
python -m black --check app tests scripts frontend
python -m ruff check app tests scripts frontend
```

项目已配置 GitHub Actions。每次 push 或 pull request 到 `main` 分支时，CI 会安装依赖并运行 Black、Ruff 和 pytest。

## Docker 说明

Dockerfile 默认启动 FastAPI 后端。Docker Compose 同时启动：

- `backend`：FastAPI，端口 `8000`。
- `frontend`：Streamlit，端口 `8501`。

Compose 中挂载 `./data:/app/data`，便于查看输出结果。前端容器通过 `API_BASE_URL=http://backend:8000` 调用后端。

## 项目阶段

- 第一阶段：工程化基础，包括项目骨架、测试、FastAPI、Streamlit、Docker、CI。
- 第二阶段：实验平台化，包括 run history、run detail、多算法对比实验和指标图表。
- 第三阶段：LangGraph / LangSmith / LLM 智能化，包括 LLM 配置层、FakeLLM、实验配置抽取、LangGraph 工作流、LangSmith 可选 tracing、错误诊断、Agent Evaluation 和前端智能 Agent 页面。
- 第四阶段：真实论文代码复现增强，后续计划包括更复杂数据集管理、论文代码环境管理、评估协议管理和更真实的 LLM Agent 工具选择。

## 当前限制

- 当前主要支持 demo 图像处理实验和传统图像处理方法。
- 当前论文输入主要支持 `.txt` 和 `.md`，暂不支持 PDF 解析。
- 当前 LLM 默认是 FakeLLM，不代表真实模型推理能力。
- 当前不能保证自动复现任意真实论文。
- 真实论文代码复现仍需要处理数据集下载、依赖冲突、CUDA 环境、随机种子、评估协议、模型权重和论文代码质量等问题。
- 深度学习图像复现模型尚未接入。

## 后续方向

- PDF 论文解析。
- embedding RAG 与 FAISS / Chroma。
- 真实 LLM provider 接入。
- 自动生成实验 YAML。
- 深度学习模型复现实验管理。
- 更完整的报告模板和可视化面板。

## 求职与展示材料

- [简历项目描述](docs/resume_description.md)
- [面试讲解材料](docs/interview_notes.md)
- [项目展示指南](docs/project_showcase.md)
