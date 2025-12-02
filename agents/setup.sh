#!/bin/bash

# Multi-Agent 系統安裝腳本

echo "=========================================="
echo "Multi-Agent 自動內容更新系統 - 安裝"
echo "=========================================="
echo ""

# 檢查 Python 版本
echo "檢查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 Python 3"
    exit 1
fi

# 創建虛擬環境
echo ""
echo "創建 Python 虛擬環境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ 虛擬環境已創建"
else
    echo "✓ 虛擬環境已存在"
fi

# 激活虛擬環境
echo ""
echo "激活虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo ""
echo "安裝 Python 依賴..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ 依賴安裝成功"
else
    echo "✗ 依賴安裝失敗"
    exit 1
fi

# 創建必要的目錄
echo ""
echo "創建必要的目錄..."
mkdir -p logs
mkdir -p ../src/content/posts
echo "✓ 目錄已創建"

# 複製配置文件
echo ""
echo "設置配置文件..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ 已創建 .env 文件，請編輯並添加你的 API key"
else
    echo "✓ .env 文件已存在"
fi

# 驗證 Git 倉庫
echo ""
echo "驗證 Git 倉庫..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✓ Git 倉庫已就緒"
else
    echo "⚠ 警告: 不在 Git 倉庫中"
fi

# 完成
echo ""
echo "=========================================="
echo "安裝完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 編輯 .env 文件並添加你的 ANTHROPIC_API_KEY"
echo "2. 運行測試: python orchestrator.py"
echo "3. 查看文檔: cat README.md"
echo ""
echo "快速開始:"
echo "  source venv/bin/activate    # 激活虛擬環境"
echo "  python orchestrator.py      # 啟動交互式模式"
echo ""
