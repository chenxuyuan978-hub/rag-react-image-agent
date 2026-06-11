# 简历项目描述

## 1. 简历项目名称

基于 RAG 与 ReAct 的图像处理论文复现实验分析 Agent

## 2. 技术栈

Python、OpenCV、Pillow、NumPy、pandas、matplotlib、scikit-image、scikit-learn、PyYAML、FastAPI、Streamlit、pytest、Black、Ruff、GitHub Actions、Docker、Docker Compose

## 3. 简历描述

### 简短版

基于 Python 构建图像处理论文复现实验分析 Agent，支持本地 RAG 检索论文实验设置、规则驱动 ReAct 工具调用、图像处理实验运行、MSE/PSNR/SSIM 指标计算、Markdown 报告生成和 run_id 实验归档，并提供 FastAPI 后端、Streamlit 前端、Docker Compose 部署和 CI 自动测试。

### 标准版

设计并实现一个面向图像处理论文复现的本地实验平台。系统使用 TF-IDF RAG 检索 `.txt/.md` 论文中的实验设置，通过规则驱动 ReAct Agent 串联检索、实验运行、指标分析和报告生成流程。实验模块支持 Gaussian Blur、Median Blur、Sharpen、Edge Detection、Histogram Equalization 等传统图像处理方法，并计算 MSE、PSNR、SSIM 指标。项目进一步实现 run_id 实验归档、历史实验查询、实验详情查看、多算法对比实验和指标对比图表。工程侧提供 FastAPI 接口、Streamlit 前端、pytest 测试、Black/Ruff 代码检查、GitHub Actions CI 和 Docker Compose 部署。

### 面试展开版

该项目从课程 MVP 逐步演进为一个较完整的实验平台。第一阶段先实现可运行闭环：论文文本加载、TF-IDF 检索、图像处理实验、指标计算、Markdown 报告和规则驱动 ReAct Agent。第二阶段补齐工程化和平台化能力，包括 FastAPI 后端、Streamlit 前端、run_id 实验归档、历史实验列表、run detail、Docker Compose 部署和 CI 自动检查。为了让实验结果更适合分析和展示，又增加了多算法对比实验，可以对同一输入图像批量运行多个方法，并自动生成 `comparison_metrics.csv` 和 MSE、PSNR、SSIM 对比图。

项目的重点不是堆叠大模型能力，而是把论文复现实验拆成清晰、可测试、可扩展的工程模块。RAG 和 ReAct 在 MVP 阶段分别使用 TF-IDF 和规则驱动实现，保证离线可运行和结果可控；后续可以平滑升级为 embedding 检索和 LLM Agent。

## 4. 项目亮点

### RAG

- 支持本地 `.txt/.md` 论文加载；
- 使用固定长度 chunk 保留来源文件和 chunk_id；
- 使用 TF-IDF 构建轻量级本地检索；
- 为后续 embedding + FAISS / Chroma 留出接口空间。

### ReAct

- 使用 Thought / Action / Observation / Final Answer 记录执行轨迹；
- 工具层封装 RAG 检索、实验运行、指标分析和报告生成；
- MVP 阶段规则驱动，避免 LLM 输出不稳定；
- 后续可替换为真正 LLM 推理和动态工具选择。

### 图像处理

- 支持 Gaussian Blur、Median Blur、Sharpen、Edge Detection、Histogram Equalization；
- 使用 OpenCV 实现基础图像处理；
- 图像读取和保存兼容 Windows 中文路径；
- 支持 MSE、PSNR、SSIM 指标计算。

### FastAPI

- 提供实验运行、Agent 运行、对比实验、历史查询和详情查询接口；
- 使用 Pydantic schema 组织请求和响应；
- 对路径穿越、文件不存在和配置错误做清晰异常处理；
- 可通过 Swagger UI 查看和调试接口。

### Docker

- 使用 Dockerfile 构建统一运行环境；
- 使用 Docker Compose 同时启动 FastAPI 后端和 Streamlit 前端；
- OpenCV 使用 headless 版本，降低系统依赖；
- 便于部署和演示。

### run_id 实验归档

- 每次实验创建独立 run 目录；
- 避免结果覆盖；
- 归档配置、输出图片、指标、报告和 trace；
- 支持历史实验列表和实验详情查看。

### 多算法对比

- 支持同一输入图像批量运行多个算法；
- 自动生成 `comparison_metrics.csv`；
- 自动生成 MSE、PSNR、SSIM 对比图；
- 便于分析不同方法在同一实验设置下的效果差异。

### pytest / CI

- 使用 pytest 覆盖核心模块、异常输入、API 和前端导入；
- 使用 Black 和 Ruff 保证代码风格；
- GitHub Actions 在 push 和 pull request 时自动运行测试与代码质量检查；
- 提升项目可维护性和交付可信度。

## 5. 面试可讲点

### 为什么先做 MVP

先做 MVP 是为了尽快形成可运行闭环。图像处理论文复现涉及论文读取、实验执行、指标计算、报告生成等多个环节，如果一开始就接入 PDF、LLM、向量数据库和前端，很容易做成不可调试的大系统。MVP 先保证每个模块可运行、可测试，再逐步扩展工程能力。

### 为什么使用 TF-IDF

TF-IDF 不需要网络、不依赖外部模型，适合课程项目和本地演示。它的结果透明，便于测试和调试。对于包含明确关键词的实验设置，例如 Gaussian blur、kernel size、PSNR、SSIM，TF-IDF 已经能满足 MVP 检索需求。后续如果需要语义理解，可以替换为 embedding 检索。

### 为什么要做 run_id

实验平台最重要的是可追溯。没有 run_id 时，多次运行会覆盖旧结果，很难比较不同配置和不同时间的实验输出。run_id 让每次运行都有独立目录，可以归档配置、图片、指标、报告和 trace，方便前端展示历史实验，也方便问题排查。

### 如何保证可复现

项目通过 YAML 配置记录实验输入、操作序列、参数、指标和输出目录；通过 run_id 保存每次运行的配置和结果；通过 summary、metrics、report 和 trace 记录实验产物；通过 pytest 和 CI 保证核心逻辑稳定。这样既能复现一次实验，也能回看历史运行过程。

### 后续如何升级为 embedding RAG 和 LLM Agent

RAG 层可以把 `TfidfRetriever` 替换为 embedding retriever，并使用 FAISS 或 Chroma 管理向量索引。ReAct 层可以把当前固定流程替换为 LLM 决策，让模型根据任务动态选择工具、解析论文实验设置并生成更自然的分析报告。由于当前工具层已经把检索、实验、指标和报告封装成明确接口，升级时不需要重写底层图像处理逻辑。
