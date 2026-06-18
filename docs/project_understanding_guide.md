# 项目理解与复盘指南：从能跑到真正掌握

这份文档面向项目小白，目标是帮助你从“按照 Codex 指令把项目做出来”，过渡到“真正理解项目架构、代码流程、Agent 设计、调试方法和面试表达”。

本项目当前已经有比较多模块：`app/api`、`frontend`、`app/react`、`app/graph`、`app/rag`、`app/llm`、`app/experiments`、`app/image_ops`、`app/reports`、`app/evaluation`、`app/observability`、`tests`、`scripts`、Docker 和 CI。第四阶段的重点不是继续堆功能，而是把这些模块真正吃透。

## 一、为什么需要第四阶段“项目理解与复盘”

使用 Codex / AI 辅助开发是正常的。现实开发里，工程师也会使用 IDE、文档、搜索、AI 工具来提高效率。关键不在于“是不是 AI 帮你写过”，而在于你是否理解最终项目。

如果你不了解代码逻辑、模块职责、数据流和调试方式，面试中会有很大风险：

- 面试官问“点击按钮后发生了什么”，你说不清楚；
- 问“后端接口在哪里”，你找不到 `app/api/main.py`；
- 问“LangGraph 和 ReAct 的区别”，你只会背概念；
- 问“为什么 Docker 里不能用 localhost 访问后端”，你不知道原因；
- 项目跑不起来时，你不知道看日志、测接口、查 import 错误。

第四阶段的目标是理解已有项目，而不是继续堆功能。

理解的标准不是背代码，而是做到：

- 能讲清楚：知道模块职责和调用链；
- 能跑通：会启动测试、后端、前端、Docker；
- 能排错：能根据报错定位问题；
- 能小改：能独立完成一个小功能修改。

## 二、重新定义项目阶段路线

| 阶段 | 名称 | 目标 | 当前内容 |
| --- | --- | --- | --- |
| 第一阶段 | 工程化基础 | 让项目能跑起来，形成基本工程结构 | 图像处理、指标计算、实验配置、报告生成、FastAPI、Streamlit、Docker、CI |
| 第二阶段 | 实验平台化 | 从一次性 demo 变成实验管理平台 | 实验历史、实验详情、多算法对比、指标图表、前端增强 |
| 第三阶段 | LangGraph / LangSmith / LLM 智能化 | 让项目具备 Agent 工作流能力 | LLM 配置层、FakeLLM、实验配置抽取、LangGraph workflow、LangSmith tracing、失败诊断、Agent Evaluation、智能 Agent 前端 |
| 第四阶段 | 项目理解与复盘 | 系统理解代码、架构、数据流、调试方式和面试表达 | 当前阶段重点 |
| 第五阶段 | 真实论文代码复现增强 | 后续再扩展到更真实的论文代码复现 | 真实论文、数据集、依赖、CUDA/PyTorch、复现实验协议 |

第四阶段先把已有项目讲清楚、跑熟、改明白。不要急着进入第五阶段。

## 三、项目整体架构小白解释

最通俗地说，这个项目做的是：

1. 用户在 Streamlit 页面输入任务；
2. 前端调用 FastAPI；
3. FastAPI 调用规则 ReAct Agent 或 LangGraph Agent；
4. Agent 调用 RAG、LLM 抽取、实验运行、指标分析、报告生成；
5. 系统输出 `metrics.csv`、`summary.json`、`report.md` 和图像结果；
6. 前端把结果展示给用户。

```text
用户
  -> Streamlit 前端 frontend/streamlit_app.py
  -> FastAPI 后端 app/api/main.py
  -> LangGraph Agent app/graph/workflow.py
  -> RAG / LLM / 实验运行 / 指标分析 / 报告生成
  -> data/outputs 和 data/runs
  -> 前端展示 final_answer、steps、report_path、diagnosis
```

规则 ReAct Agent 是稳定 baseline，位于 `app/react`。LangGraph Agent 是第三阶段新增的智能工作流，位于 `app/graph`。它们不是互相替代，而是新旧两条路径并存。

## 四、项目目录阅读顺序

不要按字母顺序看代码。建议按“从入口到主线，再到底层工具”的顺序读。

### 第 1 层：先看入口

| 文件 | 要看什么 |
| --- | --- |
| `README.md` | 项目目标、运行方式、当前能力和限制 |
| `docker-compose.yml` | 后端和前端如何一起启动，特别是 `API_BASE_URL=http://backend:8000` |
| `app/api/main.py` | FastAPI 接口入口，重点看 `/api/agent/langgraph/run` |
| `app/api/schemas.py` | API 请求和响应模型 |
| `frontend/streamlit_app.py` | Streamlit 五个 Tab，特别是“智能 Agent”页面 |

### 第 2 层：看 Agent 主线

| 文件 | 要看什么 |
| --- | --- |
| `app/react/agent.py` | 旧版规则 ReAct Agent 如何按固定顺序调用工具 |
| `app/react/tools.py` | `RagRetrieveTool`、`RunExperimentTool`、`AnalyzeMetricsTool`、`GenerateReportTool` |
| `app/react/trace.py` | Thought / Action / Observation / Final Answer 如何记录 |
| `app/graph/state.py` | `GraphAgentState` 里保存了哪些字段 |
| `app/graph/nodes.py` | 每个 LangGraph 节点具体做什么 |
| `app/graph/workflow.py` | 节点如何连接，错误时如何走分支 |
| `app/graph/error_handling.py` | 错误分类、诊断和重试判断 |

旧版 ReAct Agent 负责稳定工具链 baseline；新版 LangGraph Agent 负责更清晰的节点式智能工作流。

### 第 3 层：看 Agent 用到的工具能力

| 目录/文件 | 要看什么 |
| --- | --- |
| `app/rag/loader.py` | 如何读取 txt/md 论文 |
| `app/rag/chunker.py` | 如何把文档切成 chunk |
| `app/rag/retriever.py` | 如何用 TF-IDF 检索 |
| `app/llm/config.py` | LLM 环境变量如何加载 |
| `app/llm/client.py` | 如何选择 LLM client |
| `app/llm/fake_client.py` | FakeLLM 为什么不需要 API Key |
| `app/llm/extractors.py` | `ExperimentSpec` 如何抽取 method、params、metrics |
| `app/experiments/config_schema.py` | YAML 实验配置如何读取和校验 |
| `app/experiments/experiment_runner.py` | 单次实验如何运行 |
| `app/image_ops/image_loader.py` | 图片如何读取，兼容中文路径 |
| `app/image_ops/processors.py` | 图像处理函数 |
| `app/image_ops/metrics.py` | MSE、PSNR、SSIM |
| `app/reports/report_generator.py` | Markdown 报告如何生成 |

注意：项目没有 `app/metrics` 目录，指标代码在 `app/image_ops/metrics.py`。

### 第 4 层：看实验平台化能力

| 文件 | 要看什么 |
| --- | --- |
| `app/core/run_manager.py` | 如何创建 run_id 和 run_dir |
| `app/core/run_history.py` | 如何列出历史实验 |
| `app/core/run_detail.py` | 如何读取某次实验详情 |
| `app/experiments/comparison_runner.py` | 多算法对比实验如何运行 |
| `app/reports/comparison_charts.py` | 指标对比图如何生成 |
| `frontend/streamlit_app.py` | 历史实验和多算法对比页面如何展示 |

### 第 5 层：看工程化与验证

| 路径 | 作用 |
| --- | --- |
| `tests/` | pytest 测试，验证核心模块、API、前端导入和 Agent workflow |
| `scripts/` | demo 和辅助脚本，例如 `run_langgraph_demo.py`、`run_agent_evaluation.py` |
| `.github/workflows/ci.yml` | GitHub Actions CI |
| `Dockerfile` | 后端镜像构建方式 |
| `docker-compose.yml` | 后端和前端如何一起启动 |
| `pyproject.toml` | Black / Ruff 配置 |

## 五、重点模块逐个解释

### 1. FastAPI 后端

小白解释：API 是前端和后端的连接点。前端不会直接运行实验逻辑，而是把请求发给 FastAPI。

重点文件：

- `app/api/main.py`
- `app/api/schemas.py`

重点看智能 Agent API：

```text
POST /api/agent/langgraph/run
```

请求参数来自 `LangGraphAgentRunRequest`：

- `task`
- `config_path`
- `paper_dir`

返回结果来自 `LangGraphAgentRunResponse`：

- `final_answer`
- `report_path`
- `error`
- `error_type`
- `diagnosis`
- `retry_count`
- `metrics_analysis`
- `extracted_spec`
- `steps`
- `langsmith_tracing_enabled`
- `paper_context_count`

出错时，如果 workflow 内部能捕获错误，API 不直接 500，而是返回 `error` 和 `diagnosis`，前端可以展示给用户。

面试可能问：

- 前端点击智能 Agent 后调用哪个接口？
- 为什么错误 workflow 不直接返回 500？
- 请求和响应字段分别有什么？

### 2. Streamlit 前端

小白解释：Streamlit 是用户看到的页面。当前入口是 `frontend/streamlit_app.py`。

当前页面：

- 单次 Agent 实验：上传论文和图像，运行规则 ReAct Agent；
- 历史实验：展示 `data/runs` 下的历史 run；
- 多算法对比实验：运行 comparison YAML，展示指标表和图；
- 智能 Agent：调用 FastAPI 的 LangGraph Agent API；
- 项目说明：展示项目能力。

Docker 下前端访问后端不能随便用 `localhost`。因为在容器里，`localhost` 指的是当前容器自己。`docker-compose.yml` 中设置了：

```yaml
API_BASE_URL=http://backend:8000
```

这样 frontend 容器才能通过服务名访问 backend 容器。

面试可能问：

- `API_BASE_URL` 是干什么的？
- 为什么 Docker 里 `localhost:8000` 可能不对？
- 智能 Agent 页面展示哪些字段？

### 3. 规则 ReAct Agent

小白解释：规则 ReAct Agent 是固定流程工具调用，不靠 LLM 自己决定下一步。

重点文件：

- `app/react/agent.py`
- `app/react/tools.py`
- `app/react/trace.py`

工具包括：

- `RagRetrieveTool`
- `RunExperimentTool`
- `AnalyzeMetricsTool`
- `GenerateReportTool`

它适合作为稳定 baseline，因为流程固定、结果更容易测试。

面试可能问：

- 为什么保留旧版 ReAct？
- ReAct trace 里记录了什么？
- 每个 Tool 的职责是什么？

### 4. LangGraph Agent

小白解释：LangGraph 把 Agent 拆成 State、Node、Edge。State 保存上下文，Node 做具体工作，Edge 决定下一步走向。

重点文件：

- `app/graph/state.py`
- `app/graph/nodes.py`
- `app/graph/workflow.py`
- `app/graph/error_handling.py`

`GraphAgentState` 主要保存：

- `task`
- `config_path`
- `paper_dir`
- `paper_context`
- `extracted_spec`
- `experiment_result`
- `metrics_analysis`
- `report_path`
- `final_answer`
- `error`
- `error_type`
- `diagnosis`
- `retry_count`
- `max_retries`
- `failed_node`
- `steps`

正常流程：

```text
retrieve_paper_context
  -> extract_experiment_spec
  -> run_experiment
  -> analyze_metrics
  -> generate_report
```

错误流程：如果 `run_experiment`、`analyze_metrics` 或 `generate_report` 失败，就进入 `diagnose_error`，必要时经过 `retry_failed_step` 再重试一次。

面试可能问：

- State 里为什么要保存 `steps`？
- LangGraph 比固定顺序调用多了什么？
- 错误节点怎么走？

### 5. LLM / FakeLLM

小白解释：LLM 配置层让项目以后可以替换真实模型，但现在默认用 FakeLLM。

重点文件：

- `app/llm/config.py`
- `app/llm/client.py`
- `app/llm/fake_client.py`
- `app/llm/extractors.py`

为什么默认使用 FakeLLM：

- 不需要真实 API Key；
- 不依赖网络；
- 输出稳定；
- 适合测试和 CI。

`ExperimentSpec` 在 `app/llm/extractors.py` 中，包含：

- `method`
- `params`
- `metrics`
- `raw_response`

论文片段会先拼成 prompt，FakeLLM 返回稳定 JSON，然后解析出 `gaussian_blur`、`kernel_size=5`、`mse/psnr/ssim`。

面试可能问：

- FakeLLM 和真实 LLM 的区别？
- 为什么测试不应该依赖真实 LLM？
- `ExperimentSpec` 有什么用？

### 6. RAG 检索

小白解释：RAG 负责从本地论文资料中找和任务相关的片段。

重点文件：

- `app/rag/loader.py`
- `app/rag/chunker.py`
- `app/rag/retriever.py`

流程：

```text
data/papers 中的 txt/md
  -> Document
  -> Chunk
  -> TfidfRetriever
  -> RetrievalResult
  -> paper_context
```

当前使用 TF-IDF，所以适合关键词明确的场景。如果中文 query 和英文论文片段没有共享词，score 可能为 0。比如 query 全是中文，而论文片段是英文 `Gaussian blur kernel size PSNR`，词表重合少，TF-IDF 就难以匹配。

面试可能问：

- 为什么先用 TF-IDF？
- TF-IDF 的限制是什么？
- 后续怎么升级 embedding RAG？

### 7. 图像处理实验

小白解释：实验运行器读取 YAML 配置，然后按顺序处理图像，保存结果和指标。

重点文件：

- `app/experiments/config_schema.py`
- `app/experiments/experiment_runner.py`
- `app/image_ops/image_loader.py`
- `app/image_ops/processors.py`
- `app/image_ops/metrics.py`

输入配置示例：

```text
examples/demo_config.yaml
```

输出通常在：

```text
data/outputs/{experiment_name}/
```

会生成：

- 输出图像，例如 `step_01_gaussian_blur.png`；
- `metrics.csv`；
- `summary.json`。

面试可能问：

- YAML 配置里有哪些字段？
- 图像保存如何兼容 Windows 中文路径？
- 未知 operation 怎么处理？

### 8. 指标分析

指标代码在 `app/image_ops/metrics.py`。

| 指标 | 含义 | 趋势 |
| --- | --- | --- |
| MSE | 均方误差，衡量像素差异 | 越低越好 |
| PSNR | 峰值信噪比，常用于图像质量评价 | 越高越好 |
| SSIM | 结构相似度，衡量结构和视觉相似性 | 越接近 1 越好 |

LangGraph 中 `analyze_metrics_node` 会读取 `metrics.csv`，生成简单指标分析文本。

面试可能问：

- MSE 和 PSNR 的关系是什么？
- 为什么 SSIM 比纯像素误差更接近视觉感受？
- 如果没有 reference image，指标能不能算？

### 9. 报告生成

重点文件：

- `app/reports/report_generator.py`

`report.md` 的输入来自：

- `summary.json`
- `metrics.csv`
- `paper_context`

报告包含实验名称、实验目的、配置摘要、图像处理流程、输出图像路径、评价指标结果、论文相关片段、结果分析和结论。

面试可能问：

- report.md 是怎么生成的？
- paper_context 如何进入报告？
- 如果没有 metrics_path 怎么办？

### 10. 错误诊断与重试

重点文件：

- `app/graph/error_handling.py`
- `app/graph/nodes.py`
- `app/graph/workflow.py`

`classify_error` 会把错误文本分类：

- `config_error`
- `file_not_found`
- `experiment_error`
- `metrics_error`
- `report_error`
- `unknown_error`

`diagnosis` 是结构化诊断结果，包含错误类型、失败节点、原始信息、可能原因、建议操作和是否可重试。

哪些错误可以重试：文件缺失、实验错误、指标错误、报告错误有时可重试；配置错误通常需要用户修正。

`max_retries` 不能无限大，否则可能因为同一个错误反复运行，形成死循环。当前默认最大重试 1 次。

面试可能问：

- 如何避免无限重试？
- 为什么 config_error 不自动重试？
- diagnosis 对前端有什么价值？

### 11. LangSmith

重点文件：

- `app/observability/langsmith_config.py`

LangSmith 不是业务功能，而是可观测性能力。它帮助查看 trace、调试 Agent 执行链路。

项目默认关闭 LangSmith，因为本地运行、CI 和 Docker 不应该强制依赖外部 API Key。

开启方式：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=你的 Key
LANGSMITH_PROJECT=rag-react-image-agent
```

面试可能问：

- LangSmith 和 LangGraph 的关系是什么？
- 为什么默认关闭？
- 没有 API Key 会不会影响运行？

### 12. Agent Evaluation

重点文件：

- `app/evaluation/cases.py`
- `app/evaluation/runner.py`
- `scripts/run_agent_evaluation.py`

Agent Evaluation 和 pytest 的区别：

- pytest 检查函数、模块、API 是否正确；
- Agent Evaluation 检查完整 Agent 工作流是否按预期走完。

`AgentEvaluationCase` 描述一个评估样例，包括任务、配置、期望节点、期望输出和是否期望错误。

`AgentEvaluationResult` 描述评估结果，包括实际节点、缺失节点、缺失输出、错误类型和报告路径。

它比单纯跑 demo 更工程化，因为它可以重复验证“工作流行为”。

面试可能问：

- 为什么 demo 不等于 evaluation？
- EvaluationCase 里要检查哪些字段？
- 如何新增一个评估样例？

## 六、数据流详细 walkthrough

下面按“点击智能 Agent 按钮”开始讲。

1. 用户在 `frontend/streamlit_app.py` 的智能 Agent 页面输入 `task`、`config_path`、`paper_dir`。
2. 前端函数 `run_langgraph_agent_via_api` 向 FastAPI 发送 POST 请求。
3. FastAPI 中 `app/api/main.py` 的 `/api/agent/langgraph/run` 接收请求。
4. API 调用 `run_langgraph_agent(task, config_path, paper_dir)`。
5. `app/graph/workflow.py` 初始化 `GraphAgentState`，写入 task、config_path、paper_dir、空 paper_context、空 result、retry_count 等字段。
6. `retrieve_paper_context` 节点调用 `app/rag`，从 paper_dir 读取论文、切块、TF-IDF 检索，把结果文本放进 `paper_context`。
7. `extract_experiment_spec` 节点调用 `app/llm/extractors.py`，默认通过 FakeLLM 抽取 method、params、metrics，写入 `extracted_spec`。
8. `run_experiment` 节点读取 YAML，调用 `app/experiments/experiment_runner.py` 执行图像处理实验。
9. 实验运行器调用 `app/image_ops/image_loader.py` 读取图像，调用 `app/image_ops/processors.py` 处理图像，调用 `app/image_ops/metrics.py` 计算指标。
10. 实验输出图像、`metrics.csv` 和 `summary.json`。
11. `analyze_metrics` 节点读取 `metrics.csv`，生成 MSE / PSNR / SSIM 的简单分析文本。
12. `generate_report` 节点调用 `app/reports/report_generator.py`，根据 summary、metrics 和 paper_context 生成 `report.md`。
13. 如果某个关键节点失败，workflow 写入 `error` 和 `failed_node`，进入 `diagnose_error`，生成 `diagnosis`。
14. 最终 state 返回给 FastAPI。
15. FastAPI 整理出 `final_answer`、`steps`、`report_path`、`diagnosis`、`extracted_spec`、`metrics_analysis` 等字段。
16. Streamlit 前端展示结果。

## 七、小白 7 天学习计划

### Day 1：项目能跑起来

学习目标：知道如何启动、测试、访问前后端。

要看的文件：

- `README.md`
- `docker-compose.yml`
- `requirements.txt`

要运行的命令：

```bash
python -m pytest
docker compose up --build
```

访问：

- [http://localhost:8000/docs](http://localhost:8000/docs)
- [http://localhost:8501](http://localhost:8501/)

要回答的问题：

- FastAPI docs 在哪里？
- Streamlit 有几个页面？
- Docker Compose 启动了几个服务？

小练习：

- 打开 Streamlit 的“项目说明”和“智能 Agent”页面。

### Day 2：看前后端调用链

学习目标：理解前端如何调用后端。

要看的文件：

- `frontend/streamlit_app.py`
- `app/api/main.py`
- `app/api/schemas.py`

要运行的命令：

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
python -m streamlit run frontend/streamlit_app.py
```

要回答的问题：

- 智能 Agent 页面调用哪个 API？
- 请求 JSON 包含哪些字段？
- API 返回哪些字段？

小练习：

- 把智能 Agent 页面里的 `config_path` 改成 `examples/not_exists.yaml`，观察错误诊断。

### Day 3：看旧版 ReAct Agent

学习目标：理解稳定 baseline。

要看的文件：

- `app/react/agent.py`
- `app/react/tools.py`
- `app/react/trace.py`
- `scripts/run_react_demo.py`

要运行的命令：

```bash
python scripts/prepare_demo_data.py
python scripts/run_react_demo.py
```

要回答的问题：

- ReAct Agent 有哪些 Tool？
- Trace 里记录了什么？
- 为什么说它是规则驱动？

小练习：

- 找出 `RunExperimentTool` 在哪个文件里。

### Day 4：看新版 LangGraph Agent

学习目标：理解 State、Node、Edge。

要看的文件：

- `app/graph/state.py`
- `app/graph/nodes.py`
- `app/graph/workflow.py`
- `app/graph/error_handling.py`
- `scripts/run_langgraph_demo.py`

要运行的命令：

```bash
python scripts/run_langgraph_demo.py
```

要回答的问题：

- `GraphAgentState` 有哪些字段？
- 正常流程有哪些节点？
- 错误时怎么进入 `diagnose_error`？

小练习：

- 在输出的 steps 中找到 `retrieve_paper_context` 和 `generate_report`。

### Day 5：看 LLM、RAG 和实验运行

学习目标：理解 Agent 调用的底层能力。

要看的文件：

- `app/llm/config.py`
- `app/llm/fake_client.py`
- `app/llm/extractors.py`
- `app/rag/loader.py`
- `app/rag/chunker.py`
- `app/rag/retriever.py`
- `app/experiments/config_schema.py`
- `app/experiments/experiment_runner.py`

要运行的命令：

```bash
python scripts/run_llm_extraction_demo.py
python scripts/run_rag_demo.py
python scripts/run_demo_experiment.py examples/demo_config.yaml
```

要回答的问题：

- FakeLLM 返回什么？
- TF-IDF 检索适合什么场景？
- 实验运行会生成哪些文件？

小练习：

- 打开 `data/outputs/demo_blur_experiment/metrics.csv` 和 `summary.json` 看内容。

### Day 6：看错误诊断、Agent Evaluation、测试

学习目标：理解如何验证 Agent 工作流。

要看的文件：

- `app/graph/error_handling.py`
- `app/evaluation/cases.py`
- `app/evaluation/runner.py`
- `tests/test_langgraph_error_handling.py`
- `tests/test_agent_evaluation.py`

要运行的命令：

```bash
python scripts/run_agent_evaluation.py
python -m pytest tests/test_agent_evaluation.py
```

要回答的问题：

- `missing_config_error` 为什么应该失败但 evaluation 通过？
- Agent Evaluation 和 pytest 有什么区别？
- diagnosis 里有哪些字段？

小练习：

- 新增一个只读的 evaluation case 草稿，不急着写代码，先说清楚它要检查什么。

### Day 7：自己做一个小改动

学习目标：独立完成一个小功能修改。

可选小改动：

- 在报告中增加 `extracted_spec`；
- 在智能 Agent 页面显示 `paper_context_count`，当前页面已经有该字段，可以优化展示位置；
- 新增一个简单图像处理方法；
- 优化 RAG chunk 展示；
- 改善 `final_answer` 重复显示问题。

要看的文件根据改动选择：

- 报告：`app/reports/report_generator.py`
- 前端：`frontend/streamlit_app.py`
- 图像方法：`app/image_ops/processors.py`
- RAG：`app/rag/retriever.py`

要运行的命令：

```bash
python -m pytest
python -m black --check app tests scripts frontend
python -m ruff check app tests scripts frontend
```

要回答的问题：

- 我改了哪些文件？
- 为什么这样改？
- 如何验证没有破坏已有功能？

小练习：

- 写一段 3 分钟项目讲解稿。

## 八、必须掌握的命令清单

| 命令 | 用途 |
| --- | --- |
| `python -m pytest` | 运行全部测试 |
| `python -m black --check app tests scripts frontend` | 检查代码格式 |
| `python -m ruff check app tests scripts frontend` | 检查代码规范、导入排序等 |
| `python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000` | 启动 FastAPI 后端 |
| `python -m streamlit run frontend/streamlit_app.py` | 启动 Streamlit 前端 |
| `docker compose up --build` | Docker 构建并启动前后端 |
| `docker compose ps` | 查看容器状态 |
| `docker compose logs --tail=200` | 查看最近日志 |
| `docker compose down` | 停止容器 |
| `python scripts/run_langgraph_demo.py` | 运行 LangGraph demo |
| `python scripts/run_agent_evaluation.py` | 运行 Agent Evaluation |
| `python scripts/run_llm_extraction_demo.py` | 运行 LLM 抽取 demo |
| `python scripts/run_rag_demo.py` | 运行 RAG demo |
| `python scripts/run_comparison_experiment.py examples/comparison_config.yaml` | 运行多算法对比实验 |

## 九、常见问题排查指南

### 1. 前端打开了但后端打不开

现象：智能 Agent 页面提示后端服务可能没有启动。

可能原因：FastAPI 没启动，或端口不是 8000。

检查命令：

```bash
curl http://localhost:8000/health
```

PowerShell 可用：

```powershell
Invoke-RestMethod http://localhost:8000/health
```

修复建议：启动后端：

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### 2. Docker 中前端访问后端不能用 localhost

现象：本地浏览器能打开前端，但前端调用后端失败。

可能原因：在 frontend 容器里，`localhost` 指向 frontend 容器自己。

检查命令：

```bash
docker compose config
```

修复建议：确认 `docker-compose.yml` 中 frontend 有：

```yaml
API_BASE_URL=http://backend:8000
```

### 3. FastAPI /docs 打不开

现象：[http://localhost:8000/docs](http://localhost:8000/docs) 无响应。

可能原因：后端没启动、端口被占用、启动时报错。

检查命令：

```bash
python -c "from app.api.main import app; print(app.title)"
```

修复建议：先修 import 或语法错误，再启动 uvicorn。

### 4. backend 容器退出

现象：`docker compose ps` 中 backend 状态是 exited。

可能原因：Python import 报错、依赖没安装、配置文件错误。

检查命令：

```bash
docker compose logs --tail=200 backend
```

修复建议：根据日志修复 SyntaxError、ModuleNotFoundError 或依赖问题。

### 5. ModuleNotFoundError

现象：提示找不到某个 Python 包。

可能原因：没有安装依赖，或运行的不是项目虚拟环境。

检查命令：

```bash
python -m pip install -r requirements.txt
python -m pip check
```

修复建议：激活 `.venv` 后重新安装依赖。

### 6. SyntaxError

现象：Python 启动时报语法错误。

可能原因：文件中误写了命令文本，或代码格式被破坏。

检查命令：

```bash
python -c "from app.api.main import app; print(app.title)"
```

修复建议：看报错文件和行号，修复对应 Python 文件。

### 7. requirements.txt 改了但 Docker 没更新

现象：本地能跑，Docker 里缺包。

可能原因：镜像没重新 build。

检查命令：

```bash
docker compose build --no-cache
```

修复建议：

```bash
docker compose up --build
```

### 8. GitHub Actions 本地通过但 CI 不通过

现象：本地 pytest 通过，CI 失败。

可能原因：空目录没提交、路径大小写、平台差异、依赖版本差异。

检查命令：

```bash
python -m pytest
python -m black --check app tests scripts frontend
python -m ruff check app tests scripts frontend
```

修复建议：看 CI 日志中的第一个失败点，优先修测试和路径问题。

### 9. RAG 检索 score 都是 0

现象：检索结果不相关或分数为 0。

可能原因：query 和论文片段没有共享关键词；中文 query 对英文论文片段不友好；TF-IDF 不理解语义。

检查命令：

```bash
python scripts/run_rag_demo.py
```

修复建议：使用包含关键词的 query，例如 `Gaussian blur PSNR SSIM kernel size`；后续可升级 embedding RAG。

### 10. report_path 有但前端不显示

现象：API 返回 report_path，但页面没展示报告内容。

可能原因：前端只显示路径，没有读取文件；路径是容器内路径；文件不在挂载目录。

检查命令：

```bash
dir data\outputs
```

修复建议：确认报告真实存在，Docker 下确认 `./data:/app/data` 挂载正常。

### 11. LangSmith 没有 API Key 是否影响

现象：没有配置 LangSmith。

可能原因：这是默认状态。

检查命令：

```bash
python scripts/run_langgraph_demo.py
```

修复建议：不需要修。没有 Key 时 tracing disabled，项目仍应正常运行。

### 12. FakeLLM 和真实 LLM 的区别

现象：FakeLLM 返回固定结果。

可能原因：项目默认使用 FakeLLM 保证离线可测试。

检查命令：

```bash
python scripts/run_llm_extraction_demo.py
```

修复建议：如果要接真实 LLM，需要扩展 `app/llm/client.py`，并通过环境变量配置 provider 和 API Key。

## 十、面试复盘问题清单

1. 这个项目解决什么问题？
   - 辅助图像处理论文复现实验分析，串联检索、实验、指标和报告。
2. 为什么做这个项目？
   - 兼具 Agent 概念和可验证实验流程，适合展示工程能力。
3. 项目整体架构是什么？
   - Streamlit -> FastAPI -> ReAct / LangGraph -> RAG / LLM / 实验 / 报告。
4. RAG 是怎么做的？
   - txt/md 加载、chunk、TF-IDF 检索。
5. 为什么先用 TF-IDF？
   - 离线、透明、好测试，适合 MVP。
6. TF-IDF 有什么限制？
   - 不理解语义，跨语言 query 容易匹配差。
7. ReAct 是怎么做的？
   - 规则驱动，固定调用四个工具，记录 trace。
8. ReAct 工具有哪些？
   - RAG 检索、实验运行、指标分析、报告生成。
9. 为什么保留旧版 ReAct？
   - 作为稳定 baseline，降低升级风险。
10. LangGraph 为什么引入？
    - 更适合节点、状态、条件分支、错误处理和 trace。
11. 旧版 ReAct 和新版 LangGraph 区别？
    - 一个固定顺序工具链，一个节点式 workflow。
12. LangChain / LangGraph / LangSmith 区别？
    - LangChain 是组件生态，LangGraph 是工作流图，LangSmith 是观测和评估。
13. FakeLLM 的意义是什么？
    - 无 API Key、离线、稳定、适合 CI。
14. ExperimentSpec 是什么？
    - 从论文片段抽取出的 method、params、metrics。
15. LangSmith 为什么默认关闭？
    - 避免本地、CI、Docker 依赖外部 Key。
16. Agent Evaluation 和 pytest 区别？
    - pytest 测模块，Agent Evaluation 测工作流行为。
17. 错误诊断怎么做？
    - classify_error 分类，build_error_diagnosis 生成结构化 diagnosis。
18. 哪些错误可以重试？
    - 文件、实验、指标、报告错误有时可重试；配置错误通常不可自动重试。
19. 如何避免无限重试？
    - 使用 `retry_count` 和 `max_retries`，默认最多一次。
20. FastAPI 在项目中作用是什么？
    - 封装后端能力，供前端和外部调用。
21. Streamlit 页面有哪些？
    - 单次 Agent、历史实验、多算法对比、智能 Agent、项目说明。
22. Docker 的作用是什么？
    - 统一运行环境，一键启动前后端。
23. Docker 里为什么不能随便用 localhost？
    - localhost 指当前容器，不是另一个服务容器。
24. CI 的作用是什么？
    - 自动测试和代码质量检查，提高交付可信度。
25. 如果要加新算法怎么改？
    - 改 `processors.py`、runner 映射、测试和配置示例。
26. metrics.csv 从哪里来？
    - `experiment_runner.py` 根据 metrics 计算并保存。
27. report.md 从哪里来？
    - `report_generator.py` 根据 summary、metrics、paper_context 生成。
28. 当前项目最大限制是什么？
    - 不能自动复现任意真实论文，主要是实验分析平台。
29. 第五阶段准备怎么做真实论文复现？
    - 加数据集、依赖、CUDA、代码仓库、评估协议管理。
30. 你在项目中最想强调的亮点是什么？
    - 从 MVP 到平台化再到 LangGraph Agent 的工程演进，以及测试、Docker、CI、Evaluation。
31. 如何证明项目不是只跑了一次 demo？
    - 有 pytest、Agent Evaluation、CI 和多种脚本。
32. 如果后端启动失败，你怎么排查？
    - 先 import app，查日志，再看依赖和语法错误。

## 十一、源码阅读检查表

- [ ] 我能说清楚 `app/api/main.py` 里智能 Agent API 的入口。
- [ ] 我能说清楚 `run_langgraph_agent` 的输入输出。
- [ ] 我能说清楚 `GraphAgentState` 中主要字段。
- [ ] 我能说清楚每个 LangGraph node 的作用。
- [ ] 我能解释 FakeLLM 为什么不需要 API Key。
- [ ] 我能解释 RAG 如何从 `data/papers` 检索论文片段。
- [ ] 我能解释 metrics.csv 从哪里生成。
- [ ] 我能解释 summary.json 从哪里生成。
- [ ] 我能解释 report.md 从哪里生成。
- [ ] 我能解释 Docker 前端访问后端为什么要用服务名 `backend`。
- [ ] 我能根据日志定位 SyntaxError。
- [ ] 我能根据日志定位 ModuleNotFoundError。
- [ ] 我能解释 Agent Evaluation 和 pytest 的区别。
- [ ] 我能运行 `python scripts/run_agent_evaluation.py`。
- [ ] 我能运行 `docker compose up --build`。
- [ ] 我能自己加一个小功能并补测试。

## 十二、第四阶段完成标准

只有当你能做到以下事情，才建议进入第五阶段：

1. 能画出项目整体架构图；
2. 能讲清楚前端到后端到 Agent 的调用链；
3. 能讲清楚旧版 ReAct 和新版 LangGraph 的区别；
4. 能讲清楚 LLM、RAG、实验运行、报告生成之间的关系；
5. 能看懂并解释核心代码文件；
6. 能独立运行测试和 Docker；
7. 能根据日志定位常见错误；
8. 能独立完成一个小功能修改；
9. 能用 3 分钟讲清楚项目；
10. 能用 10 分钟展开讲清楚技术细节。

## 十三、第五阶段预告

第五阶段才建议进入真实论文代码复现增强，内容包括：

- 真实论文选择；
- 真实代码仓库接入；
- 数据集管理；
- PyTorch / CUDA 环境；
- 复现实验协议；
- baseline 结果对齐；
- 论文表格指标复现；
- 更复杂的 Agent 自动化辅助。

第四阶段先理解已有项目，不急着进入真实论文复现。把当前项目讲明白、跑稳定、会排错，才是进入第五阶段的前提。
