# 简历项目描述

## 1. 项目名称

基于 RAG + ReAct / LangGraph 的图像处理论文复现实验分析 Agent

## 2. 技术栈

Python, FastAPI, Streamlit, OpenCV, NumPy, pandas, matplotlib, scikit-image, scikit-learn, PyYAML, pytest, Docker, Docker Compose, GitHub Actions, Ruff, Black, RAG, ReAct, LangGraph, LangSmith, LLM, Markdown report generation

## 3. 简历一句话版本

设计并实现一个面向图像处理论文复现实验的 Agent 平台，结合 RAG 检索、ReAct 工具链和 LangGraph 工作流，实现论文片段检索、实验运行、指标分析、报告生成与前端可视化。

## 4. 简历标准版描述

- 基于 FastAPI + Streamlit 构建图像处理论文复现实验分析平台，支持实验运行、历史实验管理、多算法对比和智能 Agent 前端展示。
- 实现本地 RAG 检索与规则 ReAct 工具链，使用 TF-IDF 从 txt/md 论文资料中检索实验设置，并串联实验运行、指标分析和 Markdown 报告生成。
- 使用 LangGraph 将论文检索、FakeLLM 实验配置抽取、实验运行、指标分析和报告生成编排为节点式工作流，保留规则 ReAct Agent 作为稳定 baseline。
- 接入可选 LangSmith tracing，支持 Agent 执行链路观测；设计错误诊断与一次性重试机制，提升工作流可解释性和失败处理能力。
- 设计 Agent Evaluation 样例验证节点执行、输出完整性和错误处理能力，并使用 Docker、GitHub Actions、pytest、Ruff、Black 提升项目可复现性和工程质量。

## 5. 面试展开版

这个项目来源于图像处理论文复现实验的实际痛点：论文中的实验设置、方法参数和评价指标往往分散在不同章节，手动复现实验需要反复查找参数、运行图像处理流程、计算指标并整理报告。我把这个过程拆成可测试的工程模块，包括本地论文检索、图像处理实验、指标计算、报告生成、历史实验归档和前端展示，形成一个面向论文复现实验分析的 Assistant，而不是宣称自动复现任意论文。

项目分三阶段演进。第一阶段完成工程化基础和最小闭环，用 TF-IDF RAG 和规则 ReAct Agent 串联检索、实验、分析和报告。第二阶段补充实验平台能力，包括 FastAPI、Streamlit、run_id 归档、历史实验、多算法对比和指标图表。第三阶段加入 LLM 配置抽象层、FakeLLM 测试模式、LangGraph 节点式工作流、可选 LangSmith tracing、错误诊断与重试、Agent Evaluation 和前端智能 Agent 页面。我的主要贡献是从模块拆分、工作流编排、错误处理、测试和部署几个层面，把课程 MVP 逐步升级成可展示、可维护的工程项目。

## 6. 简历可量化亮点

- 支持 MSE / PSNR / SSIM 三类图像评价指标。
- 支持 Gaussian Blur、Median Blur、Sharpen、Edge Detection、Histogram Equalization 五类传统图像处理方法。
- 支持历史实验归档和多算法对比实验。
- 支持 MSE、PSNR、SSIM 指标对比图表生成。
- 支持 FastAPI 后端和 Streamlit 前端展示。
- 支持 Docker Compose 一键启动后端和前端。
- 支持 GitHub Actions CI 自动运行测试和代码质量检查。
- 支持 LangGraph 工作流和规则 ReAct baseline 双路径。
- 支持可选 LangSmith tracing，默认不依赖 API Key。
- 支持 Agent Evaluation 样例，用于验证工作流节点、输出和错误处理。

## 7. 简历关键词

RAG, ReAct, LangGraph, LangSmith, Agent Workflow, FastAPI, Streamlit, OpenCV, Image Processing, Experiment Management, Markdown Report, Docker, CI, pytest
