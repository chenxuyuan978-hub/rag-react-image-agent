# 面试讲解材料

## 1. 项目背景怎么讲

这个项目面向图像处理论文复现实验。实际做论文复现时，实验设置、参数、评价指标经常分散在论文不同位置；手动复现实验还要准备图像、运行算法、计算指标、整理报告和保存结果。项目的目标是把这些步骤拆成可运行、可测试、可追踪的工程模块，用 Agent 工作流辅助完成论文复现实验分析。

可以强调：它是 Reproduction Assistant，不是自动复现任意论文的系统。

## 2. 为什么做这个项目

我想做一个既有 AI Agent 概念，又能落地到实际实验流程的项目。单纯做聊天 Agent 很难体现工程能力，而图像处理实验有明确输入、处理过程、指标和报告，非常适合做成可验证的 Agent 工作流。

项目也方便展示完整工程链路：后端 API、前端页面、Docker、CI、测试、错误处理、历史归档和评估样例。

## 3. 旧版规则 ReAct Agent 和新版 LangGraph Agent 的区别

规则 ReAct Agent 是稳定 baseline，执行顺序固定：

```text
RAG 检索 -> 实验运行 -> 指标分析 -> 报告生成
```

它不依赖 LLM，适合保证基础流程稳定。

LangGraph Agent 是第三阶段新增的节点式工作流。它把论文检索、LLM 实验配置抽取、实验运行、指标分析、报告生成、错误诊断和重试拆成节点。这样更适合扩展复杂流程，例如条件分支、失败诊断、状态追踪和 LangSmith tracing。

## 4. LangChain、LangGraph、LangSmith 的区别

LangChain 更偏向大模型应用开发的通用组件生态，比如 prompt、model、retriever、tool 等。

LangGraph 更偏向把 Agent 过程建模成图工作流，可以定义节点、状态、边和条件分支，适合复杂 Agent 流程。

LangSmith 是可观测性和评估平台，用来查看调用链、调试 trace、分析 Agent 执行过程。本项目中 LangSmith 是可选能力，默认不开启。

## 5. RAG 在项目中的作用

RAG 用来从本地论文资料中检索和任务相关的实验片段。当前支持 txt/md 文件，使用 TF-IDF 检索。对于 demo 论文里的关键词，例如 Gaussian blur、kernel size、PSNR、SSIM、MSE，TF-IDF 已经能稳定返回相关片段。

后续可以替换为 embedding RAG 和 FAISS / Chroma，但上层 Agent 流程不需要大改。

## 6. FakeLLM 为什么有必要

FakeLLM 让项目在没有真实 API Key、没有网络、CI 环境和 Docker 环境下都能稳定运行。它返回可预测的 JSON，方便测试 LLM 抽取流程和 LangGraph 工作流。

如果一开始就依赖真实 LLM，测试会受到网络、费用、模型输出随机性和 API Key 的影响，不利于做工程化验证。

## 7. LangSmith 为什么默认关闭

LangSmith 需要 API Key，并且会把 trace 上传到外部平台。为了保证本地开发、CI 和 Docker 都能无门槛运行，项目默认关闭 tracing。

如果用户设置 `LANGSMITH_TRACING=true` 且提供 `LANGSMITH_API_KEY`，就可以启用 LangSmith。没有 Key 时，系统会自动保持关闭，不影响运行。

## 8. 错误诊断与重试怎么做

LangGraph workflow 中增加了错误诊断节点。当实验运行、指标分析或报告生成失败时，workflow 不直接崩溃，而是把错误信息写入 state，并进入 `diagnose_error`。

诊断会把错误分成：

- `config_error`
- `file_not_found`
- `experiment_error`
- `metrics_error`
- `report_error`
- `unknown_error`

诊断结果包含失败节点、原始错误、可能原因、建议操作和是否可重试。当前默认最多重试一次，避免无限循环。

## 9. Agent Evaluation 和 pytest 的区别

pytest 主要检查函数、模块、API 和边界条件是否正确。

Agent Evaluation 检查完整 Agent workflow 是否按预期执行，比如是否执行了 `retrieve_paper_context`、`extract_experiment_spec`、`run_experiment`、`generate_report`，错误场景是否进入 `diagnose_error`，输出是否包含 `final_answer`、`report_path` 或 `diagnosis`。

二者是互补关系：pytest 保证模块正确，Agent Evaluation 保证工作流行为符合预期。

## 10. 项目当前限制

- 当前主要支持 demo 图像处理实验和传统图像处理算法。
- 当前论文资料支持 txt/md，不支持 PDF。
- 当前 LLM 默认是 FakeLLM，不代表真实模型推理能力。
- 当前 LangGraph 抽取结果还没有自动写回 YAML。
- 当前不能保证自动复现任意真实论文。
- 真实论文代码复现还需要处理数据集、依赖、CUDA、随机种子、模型权重和评估协议。

## 11. 后续第四阶段计划

第四阶段可以往真实论文代码复现增强方向推进：

- 支持 PDF 解析和实验表格抽取。
- 接入真实 LLM provider。
- 使用 embedding RAG 和向量数据库。
- 根据抽取结果自动生成实验 YAML。
- 管理论文代码仓库、依赖环境和运行脚本。
- 增加数据集、模型权重、CUDA 环境和评估协议管理。
- 增加更完整的报告模板和可视化对比面板。
