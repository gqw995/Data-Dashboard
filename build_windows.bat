@echo off
chcp 65001 >nul
echo ========================================
echo 广告数据分析系统 - Windows打包脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [1/4] 检查依赖包...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    pause
    exit /b 1
)

echo.
echo [2/4] 安装PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 开始打包...
python -m PyInstaller build_app.spec --clean --noconfirm
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [4/4] 打包完成！
echo.
echo 可执行文件位置: dist\广告数据分析系统.exe
echo.
echo 提示：
echo 1. 可以将 dist\广告数据分析系统.exe 复制到任何Windows电脑上运行
echo 2. 首次运行可能需要几秒钟启动时间
echo 3. 运行后会自动打开浏览器
echo.
pause

