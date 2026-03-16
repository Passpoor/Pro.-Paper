# 📚 Pro. Paper — 科研论文深度拆解系统

> 博士级科研认知训练引擎  
> 上传 PDF → 自动解析章节 → 多模块 AI 分析 → 导出精美报告

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能亮点

| 功能 | 说明 |
|------|------|
| 📄 **PDF 自动解析** | 上传任意学术论文 PDF，自动提取文本、检测章节结构 |
| 🧠 **8 大分析模块** | 引言分析、结果因果判定、方法定位、逻辑链、终局总结、风险审查、课题构建等 |
| 🔬 **认知五层分层** | 自动将每个主张归类为 事实/观察/推断/假设/不确定性 |
| ⚠️ **机制谬误防御** | 中项不周延、肯定后件、单路径风险、Rescue 分级、语言膨胀检测 |
| 📊 **Mermaid 因果图** | 自动生成可视化因果路径图，可导出为 PNG |
| 📥 **HTML 报告导出** | 一键导出精美 HTML 报告（含图表渲染、可打印） |
| 🌐 **多 LLM 支持** | 智谱 GLM / DeepSeek / OpenAI / 任何 OpenAI 兼容 API |
| 📝 **Markdown 导出** | 纯文本报告导出，方便后续编辑 |

---

## 📸 预览

### 主界面

```
┌─────────────────────────────────────────────────┐
│  📚 科研论文深度拆解系统                         │
│  上传PDF → 选择分析模块 → 填入API Key → 开始分析  │
└─────────────────────────────────────────────────┘

┌──────────┐  ┌──────────────────────────────────┐
│ ⚙️ 配置面板 │  │ 📤 第一步：上传论文 PDF           │
│          │  │                                   │
│ API 提供商 │  │ 📄 第二步：论文预览                │
│ API Key   │  │   页数 | 字符数 | Token估算       │
│ Temperature│ │   📑 章节导航                     │
│ Max Tokens│  │                                   │
│          │  │ 🔬 第三步：运行分析                │
│ 📋 分析模块│  │   ━━━ 引言 ━━━                  │
│ ☑ 整篇拆解 │  │   [AI 流式输出分析结果...]        │
│ ☐ 引言    │  │   📊 因果路径图                   │
│ ☐ 结果    │  │                                   │
│ ☐ 终局    │  │ 📥 导出 Markdown                  │
│          │  │ 📥 导出 HTML（含图表）             │
└──────────┘  └──────────────────────────────────┘
```

### 导出的 HTML 报告
- 精美排版，支持打印
- Mermaid 图表渲染为 SVG，可一键导出为 PNG
- 完全自包含，可离线查看

---

## 🚀 快速开始

### 环境要求

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.9+ | 推荐 3.10 - 3.12 |
| pip | 最新 | Python 包管理器 |
| LLM API Key | — | 智谱/DeepSeek/OpenAI 任选其一 |

> 💡 **不需要 Node.js、不需要 GPU、不需要 Docker**

### 一键安装（Windows）

```powershell
# 1. 克隆项目
git clone https://github.com/Passpoor/Pro.-Paper.git
cd Pro.-Paper

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
streamlit run app.py
```

### 一键安装（macOS / Linux）

```bash
# 1. 克隆项目
git clone https://github.com/Passpoor/Pro.-Paper.git
cd Pro.-Paper

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
streamlit run app.py
```

### 使用 Conda（推荐 Windows 用户）

```powershell
# 1. 克隆项目
git clone https://github.com/Passpoor/Pro.-Paper.git
cd Pro.-Paper

# 2. 创建 Conda 环境
conda create -n paper-analysis python=3.12 -y
conda activate paper-analysis

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
streamlit run app.py --browser.gatherUsageStats false
```

启动后浏览器自动打开 **http://localhost:8501**

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

### Step 4：导出结果

- **📥 导出 Markdown** — 纯文本格式，方便后续编辑
- **📥 导出 HTML（含图表）** — 精美排版报告，Mermaid 图表可直接导出为 PNG，支持打印

---

## 🧠 8 大分析模块详解

### 模块零：认知五层分层（自动运行）

每个分析模块自动将论文主张分层：

| 层级 | 定义 | 示例 |
|------|------|------|
| **事实层** | 已有共识，有引用支持 | "衰老是慢性肺病的主要风险因素" |
| **观察层** | 数据直接支持，无因果语言 | "p16 表达在 COPD 组中升高 2.3 倍" |
| **推断层** | 从观察推导，可能跨层 | "p16 升高驱动了 COPD 进展" |
| **假设层** | 可证伪的核心命题 | "靶向 p16 可缓解 COPD 肺衰老" |
| **不确定性层** | 因果未闭合，条件性结论 | "该通路可能存在并行补偿" |

### 模块一：引言分析

- 重构已知事实 vs 作者声明
- 识别逻辑断点（相关→因果跳跃等）
- 评估假设的可证伪性
- 检查是否存在简约替代解释

### 模块二：结果分析

**三阶段流程：**

1. 🟢 **图优先纪律** — 独立判定因果等级
2. 🟡 **文字对照** — 检测语言膨胀
3. 🔵 **因果结构评估** — 柯霍框架 + Rescue 分级

**因果等级阶梯：**
```
现象 → 相关 → 干预 → 必要性 → 充分性 → 救援 → 机制 → 闭环
```

**Rescue 强度分级：**
```
部分恢复(低) → 单向恢复(中) → 双向恢复(高) → 体内外一致(很高) → 排除并行通路(最高)
```

### 模块三：方法功能定位

对每种方法分析：
- 解决了哪个逻辑断点？
- 是否有替代方法？
- 方法迁移价值（"逻辑断点修复工具" vs "数据生成工具"）

### 模块四：整篇逻辑链

- 实验递进逻辑验证
- 证据-方法映射
- **自动生成 Mermaid 因果路径图**
- 明确判定论文因果等级

### 模块五：终局认知总结

- 整篇逻辑推进回放
- 论文推进结构识别（现象驱动型/筛选突破型/治疗导向型等）
- **逻辑功能完成图谱**（10 项功能逐项评估）
- **博士训练核心启发**（3 条可复制原则）
- 课题迁移提示

### 模块六：课题反向构建

基于论文逻辑，为你的研究方向设计研究路径：
1. 方向压缩（四要素明确化）
2. 课题类型识别
3. 逻辑功能缺口扫描
4. **最小充分路径设计**
5. 单路径风险扫描
6. 因果闭环目标设定
7. **Mermaid 因果路径图**

### 模块七：机制推理谬误防御

自动检测 9 种逻辑谬误：

| 谬误类型 | 说明 |
|---------|------|
| 中项不周延 | "A 通过 B 作用于表型" — 但未排除 A→C→表型 |
| 肯定后件 | "过表达 B 恢复了表型 → 机制成立"（错误） |
| 明星分子依附 | 借 p53/NF-κB 等高引用分子完成机制叙述 |
| 单路径机制风险 | 未考虑并行通路和冗余补偿 |
| 部分恢复 ≠ 机制成立 | 部分恢复只能证明"参与"，不能证明"唯一通路" |
| 语言膨胀 | 用 "establish/demonstrate" 描述未排他的机制 |
| 逻辑三段论断裂 | 前件/中项/结论未独立验证 |
| 机制排他性不足 | 未完成必要性/充分性/rescue 验证 |

---

## 📁 项目结构

```
Pro.-Paper/
├── app.py              # Streamlit 主界面（Web UI）
├── parser.py           # PDF 解析 + 中英文章节检测
├── llm.py              # LLM API 客户端（流式输出）
├── prompts.py          # 分析模块指令 + API 预设配置
├── SYSTEM_PROMPT.md    # 完整系统提示词（可自定义编辑）
├── requirements.txt    # Python 依赖
├── .gitignore          # Git 忽略规则
└── README.md           # 本文件
```

---

## ⚙️ 自定义系统提示词

编辑 `SYSTEM_PROMPT.md` 即可调整分析框架，无需修改代码。例如：

- 添加新的分析模块
- 修改因果等级判定标准
- 增加领域专属的评估维度
- 调整输出格式

---

## ❓ 常见问题

### Q: PDF 解析后章节检测不准？

系统支持三种论文结构：
- ✅ **标准 IMRaD**（Introduction / Methods / Results / Discussion）
- ✅ **Nature/Science 系列**（Methods 在末尾）
- ✅ **综述类论文**（全大写标题行兜底检测）
- ✅ **中文学位论文**

若检测失败，系统会自动回退到全文分析，不影响使用。

### Q: 分析结果被截断？

- 在高级设置中增大 **Max Output Tokens**
- 建议分模块逐步分析，而非一次"整篇拆解"
- 整篇拆解建议拆成「引言」+「结果」+「终局」分三次跑

### Q: Mermaid 图不显示？

- 需要网络连接（首次加载 Mermaid CDN 资源）
- 加载一次后浏览器会缓存
- 导出 HTML 文件后可离线查看（已缓存的情况）

### Q: 中文输出质量差？

- 推荐使用**智谱 GLM-4-Plus**或**DeepSeek**
- 可降低 Temperature（0.05 - 0.1）获得更稳定的输出

### Q: 如何在服务器/远程机器上运行？

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

然后通过 `http://your-server-ip:8501` 访问。

### Q: 支持哪些 PDF？

- 推荐**文本型 PDF**（文字可选中、可复制的）
- 扫描版 PDF（纯图片）需要先 OCR 处理
- 复杂双栏排版的论文提取效果可能不佳

---

## 🔧 高级配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|-------|------|
| `STREAMLIT_SERVER_PORT` | 8501 | 服务端口 |
| `STREAMLIT_SERVER_HEADLESS` | true | 无头模式 |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | false | 关闭使用统计 |

### 自定义 API 提供商

在 `prompts.py` 的 `API_PRESETS` 字典中添加：

```python
API_PRESETS["My API"] = {
    "base_url": "https://your-api.com/v1",
    "model": "your-model",
    "placeholder": "请输入 API Key",
}
```

---

## 🛠️ 技术栈

- **前端**: [Streamlit](https://streamlit.io/) — Python Web 框架
- **PDF 解析**: [PyMuPDF](https://pymupdf.readthedocs.io/) (fitz) — 高性能 PDF 文本提取
- **LLM 调用**: [OpenAI Python SDK](https://github.com/openai/openai-python) — 兼容所有 OpenAI 格式 API
- **Markdown 渲染**: [marked.js](https://marked.js.org/) — 导出 HTML 用
- **图表渲染**: [Mermaid.js](https://mermaid.js.org/) — 因果路径图 + 流程图
- **图表导出**: SVG → Canvas → PNG — 高清图表导出

---

## 📜 License

MIT License — 自由使用、修改、分发。

---

## 🙏 致谢

- [Streamlit](https://streamlit.io/) — 让 Python 数据应用开发变得简单
- [PyMuPDF](https://pymupdf.readthedocs.io/) — 强大的 PDF 处理库
- [Mermaid.js](https://mermaid.js.org/) — 文本驱动的图表渲染
- [marked.js](https://marked.js.org/) — Markdown 解析器
- 本项目的研究框架参考了 López-Otín 等人的衰老标志理论及 Kirkland 实验室的衰老细胞研究方法论

---

<p align="center">
  Made with ❤️ for researchers who think critically about science.
</p>
