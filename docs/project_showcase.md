# 项目展示指南

## 1. 项目展示路径

推荐使用 Docker Compose 启动：

```bash
docker compose up --build
```

访问地址：

- FastAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Streamlit: [http://localhost:8501](http://localhost:8501/)

如果本地直接运行，可以分别启动：

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
python -m streamlit run frontend/streamlit_app.py
```

## 2. 推荐展示流程

建议按以下顺序展示：

1. 项目说明页面：先说明项目定位是图像处理论文复现实验分析 Assistant。
2. 单次 Agent 实验：展示上传论文和图像后，规则 ReAct Agent 如何生成 trace 和报告。
3. 历史实验：展示 run_id、summary、metrics、report、trace 和输出图像。
4. 多算法对比实验：运行 `examples/comparison_config.yaml`，展示 comparison metrics 和指标对比图。
5. 智能 Agent 页面：输入 task、config_path、paper_dir，调用 LangGraph Agent API。
6. Agent Evaluation 脚本：展示固定样例如何评估工作流稳定性。
7. LangSmith tracing：如果有 API Key，可选展示；没有 Key 时说明默认关闭，不影响运行。

## 3. 面试演示脚本

可以按下面顺序讲：

1. 先说明项目目标：辅助图像处理论文复现实验分析，不宣称自动复现任意论文。
2. 打开 Streamlit 项目说明页面，快速介绍模块：RAG、ReAct、LangGraph、实验运行、指标、报告。
3. 切到智能 Agent 页面，使用默认任务运行 LangGraph Agent。
4. 展示 `steps`：说明节点包括论文检索、实验配置抽取、实验运行、指标分析和报告生成。
5. 展示 `extracted_spec`：说明当前 FakeLLM 可以稳定抽取 method、params、metrics。
6. 展示 `metrics_analysis`：说明系统会读取 `metrics.csv` 并给出简单分析。
7. 展示 `report_path`：说明报告会保存到输出目录。
8. 演示错误诊断：把 config_path 改成不存在的路径，例如 `examples/not_exists.yaml`，展示 error、error_type 和 diagnosis。
9. 打开历史实验页面，说明 run_id 归档如何帮助追踪每次运行。
10. 最后说明工程化能力：pytest、Ruff、Black、GitHub Actions、Docker Compose 和 Agent Evaluation。

## 4. 常见问题

### 为什么不是直接自动复现所有论文？

真实论文复现不仅是读论文，还涉及数据集、依赖版本、CUDA、模型权重、随机种子、评估协议和代码质量。当前项目定位是辅助图像处理论文复现实验分析，先把可控的图像处理实验流程做成稳定平台。

### 为什么默认用 FakeLLM？

FakeLLM 不需要 API Key、不依赖网络，输出稳定，适合本地开发、CI 和课程展示。它让 LLM 抽取流程和 LangGraph workflow 可以被稳定测试。

### 为什么保留旧版 ReAct？

旧版规则 ReAct 是稳定 baseline，可以在没有 LLM 的情况下验证工具链闭环。LangGraph 是增强工作流，两者共存能降低升级风险。

### 为什么用 LangGraph？

LangGraph 适合表达多节点 Agent 工作流。它能清楚管理 state、节点、条件分支、错误诊断和重试，比单纯顺序调用更适合复杂 Agent。

### Docker 启动后前端访问不了后端怎么办？

如果在 Docker 容器中，前端不能用 `localhost:8000` 访问后端，因为 `localhost` 指向前端容器自己。项目已在 `docker-compose.yml` 中设置：

```yaml
API_BASE_URL=http://backend:8000
```

如果仍然访问失败，可以检查：

- backend 容器是否启动成功；
- `docker compose logs backend` 是否有报错；
- 前端页面中的 FastAPI 服务地址是否被手动改成了错误地址。

### LangSmith 没有 API Key 是否影响运行？

不影响。LangSmith tracing 默认关闭。没有 API Key 时，系统会保持 tracing disabled，测试、后端、前端和 Docker 都可以正常运行。
