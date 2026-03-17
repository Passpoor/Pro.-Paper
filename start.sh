#!/bin/bash

echo "========================================"
echo "  Pro. Paper - 启动中..."
echo "========================================"
echo ""

cd backend

echo "[1/2] 检查依赖..."
pip install -r requirements.txt -q

echo "[2/2] 启动服务器..."
echo ""
echo "🌐 访问地址: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================"
echo ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
