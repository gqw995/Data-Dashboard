#!/bin/bash
# 广告数据分析系统 - Mac打包脚本

echo "========================================"
echo "广告数据分析系统 - Mac打包脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "[1/4] 检查依赖包..."
python3 -m pip install --upgrade pip > /dev/null 2>&1
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖包安装失败"
    exit 1
fi

echo ""
echo "[2/4] 安装PyInstaller..."
python3 -m pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "[错误] PyInstaller安装失败"
    exit 1
fi

echo ""
echo "[3/4] 开始打包..."
python3 -m PyInstaller build_app.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "[错误] 打包失败"
    exit 1
fi

echo ""
echo "[4/4] 打包完成！"
echo ""
echo "可执行文件位置: dist/广告数据分析系统"
echo ""
echo "提示："
echo "1. 可以将 dist/广告数据分析系统 复制到任何Mac电脑上运行"
echo "2. 首次运行可能需要几秒钟启动时间"
echo "3. 运行后会自动打开浏览器"
echo "4. 如果提示'无法打开，因为无法验证开发者'，请："
echo "   - 右键点击应用程序"
echo "   - 选择'打开'"
echo "   - 在弹出对话框中点击'打开'"
echo ""

