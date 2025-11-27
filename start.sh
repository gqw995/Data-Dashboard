#!/bin/bash
# 启动脚本

echo "=========================================="
echo "广告数据分析和看板系统"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖包..."
python3 -c "import flask, pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖包安装失败，请手动执行: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# 创建必要的目录
mkdir -p uploads data_cache

echo ""
echo "启动服务..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

# 启动Flask应用
python3 app.py




