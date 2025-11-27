"""
应用程序启动器
用于打包后的独立运行，自动启动服务器并打开浏览器
"""
import os
import sys
import time
import webbrowser
import threading
import socket
from app import app

def find_free_port(start_port=5000):
    """查找可用端口"""
    port = start_port
    while port < start_port + 100:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result != 0:
            return port
        port += 1
    return None

def open_browser(url):
    """延迟打开浏览器"""
    time.sleep(1.5)  # 等待服务器启动
    webbrowser.open(url)

if __name__ == '__main__':
    # 获取资源路径（打包后的路径）
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        base_path = sys._MEIPASS
        app.template_folder = os.path.join(base_path, 'templates')
        app.static_folder = os.path.join(base_path, 'static')
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 确保必要的目录存在
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data_cache', exist_ok=True)
    
    # 查找可用端口
    port = find_free_port(5000)
    if port != 5000:
        print(f"⚠️  警告: 端口5000被占用，使用端口 {port}")
    
    url = f'http://127.0.0.1:{port}'
    
    print("=" * 50)
    print("广告数据分析和看板系统")
    print("=" * 50)
    print("正在启动服务...")
    print(f"访问地址: {url}")
    print("=" * 50)
    print("提示：关闭此窗口将停止服务")
    print("=" * 50)
    print()
    
    # 在新线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # 启动Flask应用
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n正在关闭服务...")
        sys.exit(0)

