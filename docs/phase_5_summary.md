# 第五阶段总结：真实论文与源码接入

## 1. 阶段背景

前四个阶段主要围绕 demo 论文、demo 图像和可控实验配置构建 Agent 闭环：论文检索、实验运行、指标分析、报告生成、历史管理、LangGraph 工作流和前端展示。

如果项目要继续向真实论文复现实验靠近，只处理 demo 数据是不够的。真实复现任务通常至少包含两类输入：论文文件和源码材料。因此第五阶段的目标是先建立真实输入接入能力，为后续源码分析、环境规划、容器化执行和复现报告增强打基础。

第五阶段仍然坚持边界清晰：只做真实论文与源码接入，不执行源码，不安装依赖，不自动构建环境，也不声称可以自动复现任意论文。

## 2. 已完成能力

### 5.1 后端核心模块

- 新增真实论文与源码接入后端核心模块。
- 支持论文 `.txt`、`.md`、`.pdf` 文本接入。
- 支持源码 `.zip` 和本地源码目录接入。
- 创建 `data/reproduction_runs/{run_id}/` 独立 workspace。
- 生成 `paper/`、`source/`、`artifacts/`、`logs/` 子目录。
- 生成 `paper_text.txt` 和 `intake_summary.json`。
- zip 解压时做路径穿越防护。
- 添加相关 pytest 测试。

### 5.2 FastAPI 接口与 Streamlit 页面

- 新增 `POST /api/reproduction/intake`。
- 新增 `GET /api/reproduction/runs`。
- 新增 `GET /api/reproduction/runs/{run_id}`。
- Streamlit 新增 `论文源码接入` 页面。
- 支持前端创建 reproduction intake task。
- 支持展示 `run_id`、workspace、论文文本统计、源码文件统计和 summary JSON。
- 支持列出 reproduction runs。

### 5.3 文档与材料更新

- 更新 README 中的项目定位、阶段路线、真实论文与源码接入说明和当前限制。
- 完善 `docs/reproduction_intake.md`。
- 新增 `docs/phase_5_summary.md`。
- 更新系统设计文档。
- 更新简历描述和面试材料。
- 确认 `data/reproduction_runs/` 已加入 `.gitignore`。

## 3. 新增模块说明

- `app/reproduction/`：负责复现接入输入、workspace 创建串联和 summary 生成。
- `app/paper/`：负责论文文本加载，支持 txt/md/pdf。
- `app/repo/`：负责源码 zip 或源码目录接入，并统计源码文件。
- API schemas：新增 reproduction intake 请求和响应模型。
- API endpoints：新增 reproduction intake 创建、列表和详情接口。
- frontend tab：新增 Streamlit `论文源码接入` 页面。
- docs：新增和更新第五阶段说明、阶段总结、简历材料和面试材料。

## 4. 当前数据流

```text
用户输入 paper_path/source_path
  -> FastAPI POST /api/reproduction/intake
  -> run_reproduction_intake()
  -> 创建 workspace
  -> 复制论文与源码
  -> 解析论文文本
  -> 生成 intake_summary.json
  -> 前端展示结果
```

输出位置：

```text
data/reproduction_runs/{run_id}/
```

核心输出：

- `paper/paper_text.txt`
- `source/`
- `intake_summary.json`

## 5. 当前限制

- 不分析源码依赖。
- 不执行源码。
- 不部署环境。
- 不自动生成 Dockerfile。
- 不自动下载数据集或模型权重。
- 不自动对齐论文指标。
- 不自动复现任意论文。
- PDF 解析依赖可选库 `pypdf` 或 `PyPDF2`。
- 真实任务数据不进入 Git。

## 6. 对后续阶段的意义

第五阶段为第六、七阶段提供了真实输入和独立任务 workspace。

第六阶段可以在 `source/` 和 `paper_text.txt` 基础上分析源码结构、依赖文件、README 运行命令和环境需求。

第七阶段可以在独立 workspace 基础上设计容器化执行、日志采集、资源限制和任务隔离。

## 7. 验收方式

自动检查：

```bash
python -m pytest
python -m ruff check .
python -m black --check .
```

手动 API 测试：

```http
POST /api/reproduction/intake
GET /api/reproduction/runs
GET /api/reproduction/runs/{run_id}
```

Streamlit 页面测试：

- 启动 FastAPI。
- 启动 Streamlit。
- 打开 `论文源码接入` 页面。
- 输入论文路径和源码路径。
- 创建任务并查看 summary。

gitignore 检查：

- 确认 `.gitignore` 包含 `data/reproduction_runs/`。
- 不提交真实论文、源码 zip、解压源码、日志或 artifact。
