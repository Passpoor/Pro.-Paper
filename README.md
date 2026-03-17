# 📚 Pro. Paper — 科研论文深度拆解系统

> 博士级科研认知训练引擎  
> 上传 PDF → 自动解析章节 → 多模块 AI 分析 → 导出精美报告

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 界面布局

| 左侧：配置面板 | 右侧：分析流程 |
|---------------|---------------|
| **API 提供商**（智谱/DeepSeek/OpenAI/自定义） | 📤 **第一步：上传论文 PDF** |
| **API Key** 输入框 | 📄 **第二步：论文预览**（页数/字符数/Token估算 + 章节导航） |
| **Temperature** 滑块 | 🔬 **第三步：运行分析** |
| **Max Tokens** 滑块 | • AI 流式输出分析结果 |
| **📋 分析模块**（多选） | • 📊 因果路径图自动生成 |
| ☑ 整篇拆解 | |
| ☐ 引言 | |
| ☐ 结果 | 分析完成后底部出现： |
| ☐ 方法 | 📥 **导出 Markdown** |
| ☐ 逻辑链 | 📥 **导出 HTML（含图表）** |
| ☐ 终局 | |
| ☐ 风险审查 | |
| ☐ 构建课题 | |

---

## 🚀 快速开始

### 环境要求

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.9+ | 推荐 3.10 - 3.12 |
| pip | 最新 | Python 包管理器 |
| Git | 最新 | 用于克隆和更新项目 |
| LLM API Key | — | 智谱/DeepSeek/OpenAI 任选其一 |

> 💡 **不需要 Node.js、不需要 GPU、不需要 Docker**

---

### Windows 安装步骤

**第一步：打开 PowerShell**

按 `Win + X`，选择「Windows PowerShell」或「终端」

**第二步：克隆项目**

```powershell
cd C:\Users\你的用户名
git clone https://github.com/Passpoor/Pro.-Paper.git
cd Pro.-Paper
```

**第三步：创建虚拟环境**

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

> 如果提示「无法加载文件...在此系统上禁止运行脚本」，执行：
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> 然后重新运行 `.\venv\Scripts\Activate`

**第四步：安装依赖**

```powershell
pip install -r requirements.txt
```

**第五步：启动应用**

```powershell
streamlit run app.py
```

浏览器会自动打开 **http://localhost:8501**

---

### macOS / Linux 安装步骤

**第一步：打开终端**

**第二步：克隆项目**

```bash
cd ~
git clone https://github.com/Passpoor/Pro.-Paper.git
cd Pro.-Paper
```

**第三步：创建虚拟环境**

```bash
python3 -m venv venv
source venv/bin/activate
```

**第四步：安装依赖**

```bash
pip install -r requirements.txt
```

**第五步：启动应用**

```bash
streamlit run app.py
```

浏览器会自动打开 **http://localhost:8501**

---

## 🔄 如何更新

当项目发布新版本时，按以下步骤更新：

### Windows 更新步骤

```powershell
# 1. 进入项目目录
cd C:\Users\你的用户名\Pro.-Paper

# 2. 激活虚拟环境
.\venv\Scripts\Activate

# 3. 拉取最新代码（自动覆盖旧版本）
git pull origin main

# 4. 更新依赖（如有新增）
pip install -r requirements.txt

# 5. 重新启动
streamlit run app.py
```

### macOS / Linux 更新步骤

```bash
# 1. 进入项目目录
cd ~/Pro.-Paper

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 拉取最新代码（自动覆盖旧版本）
git pull origin main

# 4. 更新依赖（如有新增）
pip install -r requirements.txt

# 5. 重新启动
streamlit run app.py
```

> ⚠️ **注意**：如果你修改了 `SYSTEM_PROMPT.md`，更新时可能会提示冲突。建议先备份你的修改：
> ```bash
> cp SYSTEM_PROMPT.md SYSTEM_PROMPT_backup.md
> ```
> 更新后对比两个文件，手动合并你的自定义内容。

---

## 📖 使用指南

### Step 1：配置 API

在左侧面板选择 LLM 提供商并填入 API Key：

| 提供商 | 获取 API Key | 推荐模型 | Max Tokens |
|--------|-------------|---------|-----------|
| **智谱 AI** | [open.bigmodel.cn](https://open.bigmodel.cn) | glm-4-plus | 8192 |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com) | deepseek-chat | 8192 |
| **OpenAI** | [platform.openai.com](https://platform.openai.com) | gpt-4o | 16384 |
| 自定义 | — | 你的模型 | 视 API 而定 |

> 💡 **推荐**：中文论文用智谱 GLM-4-Plus，英文论文用 GPT-4o

### Step 2：上传论文

- 支持 **任意 PDF 格式**的学术论文
- 推荐 **文本型 PDF**（非扫描件），提取效果最佳
- 支持 50+ 页的大论文
- 自动检测中英文章节结构（摘要/引言/方法/结果/讨论/结论）

### Step 3：选择分析模块

在左侧面板勾选分析模块：

| 模块 | 功能 | 适用场景 | 预估耗时 |
|------|------|---------|---------|
| **整篇拆解** | 全流程完整分析 | 首次阅读新论文 | ~3-5 min |
| **引言** | 逻辑断点识别 | 评估论文问题质量 | ~1-2 min |
| **结果** | 因果等级判定 | 审稿/评估证据强度 | ~2-3 min |
| **方法** | 功能定位与迁移 | 学习实验方法 | ~1 min |
| **逻辑链** | 因果路径 + Mermaid 图 | 梳理论文论证框架 | ~2-3 min |
| **终局** | 认知总结 + 课题迁移 | 提炼可复制的研究方法 | ~3-4 min |
| **风险审查** | 机制谬误防御 | 审稿/自查逻辑漏洞 | ~2-3 min |
| **构建课题** | 反向构建研究路径 | 基于论文设计自己的课题 | ~2-3 min |

### Step 4：运行分析

点击「开始分析」按钮，AI 会流式输出分析结果。

### Step 5：导出报告

分析完成后，页面底部会出现导出按钮：

- **📥 导出 Markdown** — 纯文本格式，方便后续编辑
- **📥 导出 HTML（含图表）** — 精美排版报告，Mermaid 图表可直接导出为 PNG，支持打印

---

## 🧠 核心特性

### 认知五层分层（自动运行）

每个分析模块自动将论文主张分层：**事实 → 观察 → 推断 → 假设 → 不确定性**

### 机制推理谬误防御

自动检测：中项不周延、肯定后件、语言膨胀、单路径风险等 9 种逻辑谬误

### 因果等级判定

**现象 → 相关 → 干预 → 必要性 → 充分性 → 救援 → 机制 → 闭环**

---

## ⚙️ 自定义系统提示词

编辑 `SYSTEM_PROMPT.md` 即可调整分析框架，无需修改代码：

- 添加新的分析模块
- 修改因果等级判定标准
- 增加领域专属的评估维度

---

## ❓ 常见问题

### Q: PDF 解析后章节检测不准？

系统支持：标准 IMRaD、Nature/Science 系列、综述类论文、中文学位论文

### Q: 分析结果被截断？

- 增大 **Max Output Tokens**
- 建议分模块逐步分析

### Q: Mermaid 图不显示？

- 需要网络连接（首次加载 Mermaid CDN）
- 导出 HTML 后可离线查看

### Q: 中文输出质量差？

- 推荐使用**智谱 GLM-4-Plus**或**DeepSeek**
- 可降低 Temperature（0.05 - 0.1）

### Q: 更新时提示「Please commit your changes or stash them」？

这说明你有未提交的本地修改。解决方法：

```bash
# 方法1：暂存你的修改
git stash
git pull origin main
git stash pop

# 方法2：放弃本地修改（会丢失你的修改！）
git checkout .
git pull origin main
```

### Q: 如何在服务器上运行？

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

然后通过 `http://你的服务器IP:8501` 访问。

---

## 📜 License

MIT License — 自由使用、修改、分发。

---

<p align="center">
  Made with ❤️ for researchers who think critically about science.
</p>
