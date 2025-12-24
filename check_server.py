#!/usr/bin/env python3
"""
服务器诊断脚本
用于检查Flask应用是否能正常启动
"""
import sys
import os

print("=" * 50)
print("服务器诊断工具")
print("=" * 50)
print()

# 检查Python版本
print("1. 检查Python版本...")
print(f"   Python版本: {sys.version}")
if sys.version_info < (3, 7):
    print("   ⚠️  警告: 建议使用Python 3.7+")
else:
    print("   ✅ Python版本符合要求")
print()

# 检查依赖包
print("2. 检查依赖包...")
required_packages = ['flask', 'pandas', 'openpyxl', 'werkzeug']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package} 已安装")
    except ImportError:
        print(f"   ❌ {package} 未安装")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   ⚠️  缺少以下包: {', '.join(missing_packages)}")
    print("   请运行: pip3 install -r requirements.txt")
else:
    print("   ✅ 所有依赖包已安装")
print()

# 检查文件结构
print("3. 检查文件结构...")
required_files = [
    'app.py',
    'data_processor.py',
    'templates/index.html',
    'templates/dashboard.html',
    'static/css/style.css',
    'static/js/dashboard.js'
]

all_files_exist = True
for file_path in required_files:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ {file_path} 不存在")
        all_files_exist = False

if all_files_exist:
    print("   ✅ 所有必需文件存在")
else:
    print("   ⚠️  部分文件缺失，请检查项目结构")
print()

# 检查目录权限
print("4. 检查目录权限...")
directories = ['templates', 'static']
for directory in directories:
    if os.path.exists(directory):
        if os.access(directory, os.R_OK):
            print(f"   ✅ {directory}/ 可读")
        else:
            print(f"   ❌ {directory}/ 不可读")
    else:
        print(f"   ⚠️  {directory}/ 不存在")

# 检查系统临时目录权限
import tempfile
temp_dir = tempfile.gettempdir()
if os.access(temp_dir, os.W_OK):
    print(f"   ✅ 系统临时目录可写 ({temp_dir})")
else:
    print(f"   ❌ 系统临时目录不可写 ({temp_dir})")
print()

# 检查端口占用
print("5. 检查端口5000...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    if result == 0:
        print("   ⚠️  端口5000已被占用")
        print("   请关闭占用该端口的程序，或修改app.py中的端口号")
    else:
        print("   ✅ 端口5000可用")
except Exception as e:
    print(f"   ⚠️  无法检查端口: {e}")
print()

# 尝试导入应用
print("6. 检查应用导入...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import app
    print("   ✅ Flask应用可以正常导入")
    
    # 检查路由
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    print(f"   ✅ 已注册 {len(routes)} 个路由")
    print("   主要路由:")
    for route in routes[:5]:
        if not route.startswith('/static'):
            print(f"      - {route}")
except Exception as e:
    print(f"   ❌ 导入应用失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 50)
print("诊断完成！")
print("=" * 50)
print()
print("如果所有检查都通过，请运行以下命令启动服务器：")
print("  python3 app.py")
print()
print("然后访问: http://127.0.0.1:5000")
print("或者: http://localhost:5000")
print()



