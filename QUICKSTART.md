# 🚀 快速开始指南（简化版 v2.1）

## ✨ 新功能

### 方式 1：直接粘贴文本（推荐）
- ✅ 不需要上传 PDF
- ✅ 直接复制粘贴论文内容
- ✅ 即时开始分析

### 方式 2：上传 PDF（可选）
- ✅ 自动解析 PDF
- ✅ 提取文本内容

---

## 📋 使用步骤

### 1. 更新代码
```bash
cd C:\Users\13260\.openclaw-autoclaw\workspace\Pro-Paper
git pull origin refactor/native-web
```

### 2. 启动服务
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问应用
打开浏览器访问：**http://localhost:8000**

---

## 🎯 快速测试

### 方式 A：粘贴文本（最快）

1. 打开 http://localhost:8000
2. 在左侧输入 API Key
3. 在右侧文本框粘贴论文内容
4. 点击 **🚀 开始分析**

### 方式 B：上传 PDF

1. 点击"上传 PDF"标签
2. 上传 PDF 文件
3. 点击 **🚀 开始分析**

---

## 🔧 API 配置

### 智谱 AI
- API 提供商：智谱 AI
- 模型：GLM-4-Plus
- Base URL：自动填充

### DeepSeek
- API 提供商：DeepSeek
- 模型：deepseek-chat
- Base URL：自动填充

### OpenAI
- API 提供商：OpenAI
- 模型：gpt-4o
- Base URL：自动填充

---

## 📊 分析模块

- **整篇拆解** - 全文深度分析
- **引言** - 研究背景和动机
- **结果** - 核心发现和数据解读
- **方法** - 实验设计和分析方法
- **逻辑链** - 论证链条梳理
- **终局** - 研究局限和未来方向
- **风险审查** - 潜在问题和风险点
- **构建课题** - 迁移到你的研究方向

---

## ❓ 常见问题

### Q1: 端口被占用？
```bash
# 使用其他端口
python -m uvicorn main:app --reload --port 8001
```

### Q2: 依赖缺失？
```bash
cd backend
pip install -r requirements.txt
```

### Q3: 无法访问？
- 检查防火墙设置
- 确认服务已启动
- 尝试 http://127.0.0.1:8000

---

## 🎉 特点

1. **更简单** - 直接粘贴文本，无需上传
2. **更稳定** - 简化流程，减少错误
3. **更快速** - 即时开始分析
4. **更友好** - 网页格式，易于使用

---

## 📞 需要帮助？

如果遇到问题，请告诉我：
1. 具体的错误信息
2. 浏览器控制台的日志（F12 → Console）
3. 操作步骤截图

---

**Made with ❤️ for Researchers**
