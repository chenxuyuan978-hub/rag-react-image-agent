# 系统设计文档

## 1. 项目背景

图像处理论文复现实验通常需要同时处理论文阅读、实验配置、图像处理、指标计算和报告整理。对于课程项目或初步科研复现来说，常见痛点包括：

- 实验设置分散在论文的不同章节中；
- 方法参数和评价指标需要人工反复查找；
- 手动复现实验步骤较多，容易遗漏中间结果；
- 不同算法之间的对比结果难以统一管理；
- 实验报告整理耗时，且可追溯性不足。

本项目尝试构建一个本地可运行的实验分析 Agent，把“论文检索、实验执行、指标分析、报告生成、历史归档”整合为一个可测试的工程项目。

## 2. 系统目标

项目目标是构建一个基于 RAG + ReAct 的图像处理实验分析与论文复现 Agent。

系统希望实现：

- 读取本地 `.txt` / `.md` 论文资料；
- 检索论文中的实验设置、参数和评价指标；
- 根据 YAML 配置执行图像处理实验；
- 计算 MSE、PSNR、SSIM；
- 生成 Markdown 复现实验报告；
- 用 run_id 归档每次实验结果；
- 支持历史实验查看和实验详情查询；
- 支持多算法对比实验和指标对比图表；
- 通过 FastAPI 和 Streamlit 提供后端接口与前端展示。

## 3. 总体架构

系统分为以下模块：

- 用户输入模块：接收论文、图像、任务描述和 YAML 配置；
- RAG 检索模块：从论文文本中检索相关实验片段；
- ReAct Agent 模块：按 Thought / Action / Observation / Final Answer 流程调用工具；
- 图像处理实验模块：执行单次实验和多算法对比实验；
- 指标计算模块：计算 MSE、PSNR、SSIM；
- 报告与图表模块：生成 Markdown 报告和指标对比图；
- 实验归档模块：创建 run_id，记录历史实验和详情；
- FastAPI 后端模块：提供程序化接口；
- Streamlit 前端模块：提供可视化操作页面。

整体流程：

```text
用户任务 / 配置文件
        |
        v
论文加载与 RAG 检索
        |
        v
ReAct Agent 工具调用
        |
        v
图像处理实验 / 多算法对比
        |
        v
指标计算 -> 图表生成
        |
        v
报告生成 -> run_id 归档 -> API / 前端展示
```

## 4. RAG 设计

当前 RAG 模块使用 TF-IDF 作为本地检索方案，重点是降低实现复杂度并保证离线可运行。

设计流程：

- 文档加载：读取指定目录下的 `.txt` 和 `.md` 文件；
- 文本切块：按照固定长度把文档切成 chunk，保留来源文件和 chunk_id；
- 索引构建：使用 `TfidfVectorizer` 对 chunk 建立词频特征；
- 查询检索：根据任务描述或关键词返回 top-k 相关片段；
- 工具封装：通过 `RagRetrieveTool` 提供给 ReAct Agent 调用。

选择 TF-IDF 的原因：

- 不需要网络和在线 API；
- 对课程项目和 MVP 阶段足够透明；
- 便于测试；
- 后续可以替换为 embedding + FAISS / Chroma，而不改变上层 Agent 流程。

## 5. ReAct 设计

当前 ReAct 是规则驱动版本，不接入 LLM。它保留 ReAct 的结构化轨迹，方便后续替换为真正的大模型推理。

执行结构：

- Thought：记录当前步骤目标；
- Action：调用具体工具；
- Observation：记录工具返回结果；
- Final Answer：生成最终结论或失败原因。

当前工具：

- `RagRetrieveTool`：检索论文相关片段；
- `RunExperimentTool`：运行单次图像处理实验；
- `AnalyzeMetricsTool`：读取 `metrics.csv` 并输出简单指标分析；
- `GenerateReportTool`：生成 Markdown 复现实验报告。

MVP 阶段执行顺序固定：

```text
RAG 检索 -> 运行实验 -> 分析指标 -> 生成报告
```

这种设计保留了 Agent 的可解释执行轨迹，也避免一开始引入 LLM 带来的不稳定性。

## 6. 图像处理实验设计

单次实验使用 YAML 配置描述：

- `experiment_name`：实验名称；
- `input_image`：输入图像；
- `reference_image`：参考图像；
- `operations`：图像处理操作序列；
- `metrics`：评价指标；
- `output_dir`：输出目录。

实验流程：

1. 读取输入图像；
2. 按配置顺序执行图像处理操作；
3. 每一步保存输出图像；
4. 如果有参考图像，计算 MSE、PSNR、SSIM；
5. 保存 `metrics.csv`；
6. 保存 `summary.json`。

图像读取和保存兼容 Windows 中文路径：

- 读取优先使用 `numpy.fromfile + cv2.imdecode`；
- 保存优先使用 `cv2.imencode + Path.write_bytes`。

## 7. 多算法对比实验设计

多算法对比实验面向同一组输入图像和参考图像，批量运行多个处理方法。

配置文件包含：

- `comparison_name`；
- `input_image`；
- `reference_image`；
- `methods`；
- `metrics`；
- `output_dir`。

运行流程：

1. 加载输入图像和参考图像；
2. 对每个 method 单独执行图像处理；
3. 保存每个 method 的输出图像；
4. 对每个 method 计算 MSE、PSNR、SSIM；
5. 生成 `comparison_metrics.csv`；
6. 生成 MSE、PSNR、SSIM 对比图；
7. 生成 `comparison_summary.json`，记录输出图片、指标文件和图表路径。

该模块用于展示不同传统图像处理方法在同一数据上的效果差异。

## 8. run_id 实验归档设计

为了避免实验结果互相覆盖，系统引入 run_id 机制。

每次通过 API 或前端运行实验时，会创建：

```text
data/runs/{run_id}/
```

run_id 通常包含时间戳和安全化后的实验名称，例如：

```text
20260611_153000_demo_blur_experiment
```

归档目录中可以包含：

- `config.yaml` 或 `comparison_config.yaml`；
- 输出图像；
- `metrics.csv` 或 `comparison_metrics.csv`；
- `summary.json` 或 `comparison_summary.json`；
- `report.md`；
- `trace.txt`；
- 指标对比图表。

run history 模块用于列出历史实验，run detail 模块用于读取某次实验的详细结果。

## 9. FastAPI 后端设计

FastAPI 提供面向外部调用的接口层，主要负责请求校验、调用现有业务模块、返回结构化结果和处理错误。

主要接口：

- `GET /health`：健康检查；
- `POST /api/experiments/run`：运行单次实验；
- `POST /api/experiments/compare`：运行多算法对比实验；
- `POST /api/agent/run`：运行 ReAct Agent；
- `GET /api/runs`：列出历史 run；
- `GET /api/runs/{run_id}`：查看 run 摘要；
- `GET /api/runs/{run_id}/detail`：查看 run 详情；
- `GET /api/reports/{report_name}`：读取报告内容。

API 层不重复实现图像处理、RAG 或报告逻辑，只封装已有模块。

## 10. Streamlit 前端设计

Streamlit 前端用于展示项目能力，当前分为四个 tab：

- 单次 Agent 实验：上传论文和图像，运行 ReAct Agent；
- 历史实验：展示 run 列表，选择 run_id 后查看详情；
- 多算法对比实验：运行对比 YAML，展示指标表、图表和输出图像；
- 项目说明：说明当前系统能力。

前端调用已有模块：

- `run_history`；
- `run_detail`；
- `comparison_runner`；
- ReAct Agent 和工具层；
- 报告与图表模块。

前端只做交互和展示，不重复实现核心业务逻辑。

## 11. 工程化设计

项目逐步加入工程化能力：

- pytest：覆盖核心模块、API、前端导入、实验运行和异常情况；
- Black：统一代码格式；
- Ruff：静态检查和导入排序；
- GitHub Actions：push 和 pull request 时自动运行检查；
- Dockerfile：构建后端运行镜像；
- Docker Compose：同时启动 FastAPI 后端和 Streamlit 前端；
- 日志与错误处理：使用标准 logging 和自定义异常提升可维护性。

## 12. 当前限制

当前版本仍然保持本地实验平台定位，主要限制包括：

- 论文只支持 `.txt` 和 `.md`，暂不支持 PDF；
- RAG 使用 TF-IDF，不支持语义 embedding；
- ReAct 是规则驱动，不是真正的 LLM 推理；
- 图像处理只支持传统方法，不支持深度学习模型；
- 指标只支持 MSE、PSNR、SSIM；
- 报告是 Markdown 模板生成，尚未做复杂自然语言分析。

## 13. 后续优化方向

后续可以继续扩展：

- PDF 论文解析，提取正文、表格和实验章节；
- 使用 embedding + FAISS / Chroma 替换 TF-IDF；
- 接入 LLM 自动抽取实验设置；
- 使用 LLM ReAct Agent 动态选择工具；
- 支持更多图像处理和深度学习复现模型；
- 增加实验参数网格搜索；
- 增强报告模板和可视化能力；
- 支持用户管理、实验标签和结果对比面板。
