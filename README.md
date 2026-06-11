# 基于 RAG 与 ReAct 的图像处理论文复现实验分析 Agent

这是一个课程/论文项目的 MVP 版本。它可以读取本地论文资料，检索实验设置，运行基础图像处理实验，计算图像评价指标，并生成 Markdown 实验报告。

项目当前不接 OpenAI API，不使用深度学习模型，也不依赖在线服务。所有核心流程都可以在本地运行。

## 项目简介

本项目的目标是做一个“论文复现实验小助手”：

- 读取 `.txt` / `.md` 格式的图像处理论文资料；
- 使用 TF-IDF 从论文中检索实验设置；
- 根据 YAML 配置运行图像处理实验；
- 计算 MSE、PSNR、SSIM 等指标；
- 生成 Markdown 格式的实验复现报告；
- 用一个最小 ReAct Agent 串起检索、实验、分析和报告生成流程。

## 系统架构

整体流程可以理解为：

```text
用户任务
  -> RAG 检索
  -> ReAct 工具调用
  -> 实验运行
  -> 指标分析
  -> 报告生成
```

其中：

- RAG 负责从论文资料里找相关实验信息；
- ReAct 工具层负责调用检索、实验、分析、报告等功能；
- 实验运行器负责执行图像处理操作；
- 报告模块负责把结果整理成 Markdown 文件。

## 目录结构

```text
rag_react_image_agent/
├── README.md
├── requirements.txt
├── app/
│   ├── image_ops/       # 图像读取、图像处理、评价指标
│   ├── experiments/     # YAML 配置读取与实验运行器
│   ├── rag/             # 本地 TF-IDF RAG 检索
│   ├── react/           # ReAct 工具层与最小 Agent
│   └── reports/         # Markdown 报告生成
├── data/
│   ├── papers/          # 可放入 txt/md 论文资料
│   ├── images/          # Demo 输入图和参考图
│   └── outputs/         # 实验输出结果
├── examples/
│   ├── demo_config.yaml # Demo 实验配置
│   └── demo_paper.md    # Demo 论文资料
├── scripts/
│   ├── prepare_demo_data.py
│   ├── run_demo_experiment.py
│   ├── run_rag_demo.py
│   └── run_react_demo.py
└── tests/
```

## 环境准备

建议先进入项目根目录：

```bash
cd rag_react_image_agent
```

创建虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell 激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

## 运行测试

```bash
python -m pytest
```

如果看到类似 `passed` 的结果，说明当前功能可以正常运行。

## 代码质量检查

```bash
python -m black --check app tests scripts frontend
python -m ruff check app tests scripts frontend
```

## CI 自动检查

项目配置了 GitHub Actions。每次 push 或 pull request 到 `main` 分支时，CI 会自动安装依赖，并运行 Black、Ruff 和 pytest，帮助提前发现格式、静态检查和测试问题。

## 运行 Demo

先生成 Demo 图片数据：

```bash
python scripts/prepare_demo_data.py
```

运行一次普通图像处理实验：

```bash
python scripts/run_demo_experiment.py examples/demo_config.yaml
```

运行本地 RAG 检索 Demo：

```bash
python scripts/run_rag_demo.py
```

运行完整 ReAct Demo：

```bash
python scripts/run_react_demo.py
```

启动 Streamlit 前端：

```bash
streamlit run frontend/streamlit_app.py
```

启动 FastAPI 后端：

```bash
python -m uvicorn app.api.main:app --reload
```

后端启动后，可以在浏览器打开 API 文档：

```text
http://127.0.0.1:8000/docs
```

## 错误排查

如果运行失败，请优先查看终端日志。项目会把关键错误输出到控制台，方便定位是配置文件、图像文件、RAG 检索还是报告生成出了问题。

FastAPI 后端遇到错误时，会返回清晰的错误信息，例如配置缺失、文件不存在或报告路径非法等。

## 输出结果说明

运行实验后，`data/outputs/` 下会生成实验结果，例如：

- `step_01_gaussian_blur.png`：第 1 步图像处理结果；
- `step_02_sharpen.png`：第 2 步图像处理结果；
- `metrics.csv`：MSE、PSNR、SSIM 等评价指标；
- `summary.json`：实验结果摘要；
- `report.md`：Markdown 实验复现报告。

## 当前 MVP 支持功能

- 支持 `.txt` / `.md` 论文资料；
- 使用 TF-IDF 实现本地 RAG 检索；
- 使用规则驱动的最小 ReAct 流程；
- 支持基础图像处理；
- 支持 MSE、PSNR、SSIM 指标；
- 支持生成 Markdown 报告。

当前支持的图像处理操作：

- `gaussian_blur`
- `median_blur`
- `sharpen`
- `edge_detect`
- `histogram_equalization`

## 后续可扩展方向

- PDF 论文解析；
- OpenAI API 接入；
- FAISS / Chroma 向量数据库；
- 深度学习图像复现模型；
- Streamlit 前端。
