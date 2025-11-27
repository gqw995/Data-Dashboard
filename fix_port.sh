#!/bin/bash
# 修复端口占用问题的脚本

echo "=========================================="
echo "修复端口占用问题"
echo "=========================================="
echo ""

# 查找占用5000端口的进程
PID=$(lsof -ti:5000 2>/dev/null)

if [ -z "$PID" ]; then
    echo "✅ 端口5000未被占用，可以直接启动服务"
    echo ""
    echo "运行以下命令启动服务："
    echo "  python3 app.py"
    exit 0
fi

echo "⚠️  发现端口5000被占用（进程ID: $PID）"
echo ""
echo "进程信息："
ps -p $PID -o pid,command 2>/dev/null || echo "进程可能已结束"
echo ""

read -p "是否要关闭占用端口的进程？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在关闭进程 $PID..."
    kill $PID 2>/dev/null
    sleep 1
    
    # 检查是否成功关闭
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ 进程已关闭"
        echo ""
        echo "现在可以启动服务了："
        echo "  python3 app.py"
    else
        echo "⚠️  进程仍在运行，尝试强制关闭..."
        kill -9 $PID 2>/dev/null
        sleep 1
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "✅ 进程已强制关闭"
        else
            echo "❌ 无法关闭进程，请手动处理"
            echo "   或者使用其他端口（应用会自动选择可用端口）"
        fi
    fi
else
    echo "已取消操作"
    echo ""
    echo "提示：应用会自动选择其他可用端口（5001-5099）"
    echo "运行以下命令启动服务："
    echo "  python3 app.py"
fi

echo ""
echo "=========================================="



