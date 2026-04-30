# -*- coding: utf-8 -*-
"""
图形用户界面模块 (GUI)

提供测试工具的主窗口，包含：
- 启动/停止 2D/3D 环境测试
- 实时显示测试日志
- 打开测试报告
- 支持打包后通过子进程运行测试（避免递归启动）
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ctypes
import subprocess

# ==================== 高DPI适配 ====================
# 使程序在 Windows 高 DPI 显示器上正确缩放
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ==================== 测试模式入口（用于打包后子进程） ====================
# 当 exe 以 --run-test 参数启动时，进入测试模式，不显示 GUI
# 直接调用 run.run_tests() 并在当前进程中执行 pytest
if len(sys.argv) > 1 and sys.argv[1] == "--run-test":
    import run
    env = sys.argv[2] if len(sys.argv) > 2 else "2d"
    run.run_tests(env, log_callback=print, direct_mode=True)
    sys.exit(0)

# ==================== 正常 GUI 模式 ====================
import run

# ==================== 界面样式常量 ====================
BG_COLOR = "#F5F7FA"                       # 主背景色
TITLE_COLOR = "#2C3E50"                    # 标题文字颜色
DEFAULT_FONT = ("Microsoft YaHei UI", 10)  # 全局默认字体
TITLE_FONT = ("Microsoft YaHei UI", 18, "bold")  # 标题字体
BUTTON_FONT = ("Microsoft YaHei UI", 10, "bold") # 按钮字体
LOG_FONT = ("Consolas", 10)                # 日志区域字体（等宽）
STATUS_FONT = ("Microsoft YaHei UI", 9)    # 状态栏字体

def resource_path(relative_path):
    """
    获取资源文件的绝对路径（支持 PyInstaller 打包后的 _MEIPASS 目录）。
    :param relative_path: 相对于项目根目录的路径
    :return: 绝对路径
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==================== Chrome 浏览器检测（增强版） ====================
def is_chrome_installed():
    """
    检测系统中是否已安装 Google Chrome 浏览器。
    支持以下检测方式：
      1. 环境变量 PATH 中的 chrome 命令
      2. 常见安装路径（Program Files、用户目录 AppData）
      3. Windows 注册表（App Paths 和 Google Chrome 键）
    :return: 已安装返回 True，否则 False
    """
    import shutil
    import os

    # 1. 检查 PATH 中是否有 chrome 命令
    if shutil.which("chrome"):
        return True

    # 2. 检查常见安装路径（包括系统目录和用户目录）
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),   # 用户安装路径
    ]
    for path in common_paths:
        if os.path.exists(path):
            return True

    # 3. 通过注册表查找（最可靠，兼容绝大多数情况）
    try:
        import winreg
        # 尝试从 App Paths 读取（HKEY_LOCAL_MACHINE）
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
        chrome_path, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if chrome_path and os.path.exists(chrome_path):
            return True
    except:
        pass

    try:
        import winreg
        # 尝试从 App Paths 读取（HKEY_CURRENT_USER）
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
        chrome_path, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if chrome_path and os.path.exists(chrome_path):
            return True
    except:
        pass

    try:
        import winreg
        # 尝试从 Google Chrome 注册表键读取安装路径
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome")
        chrome_dir, _ = winreg.QueryValueEx(key, "Path")
        winreg.CloseKey(key)
        exe_path = os.path.join(chrome_dir, "chrome.exe")
        if os.path.exists(exe_path):
            return True
    except:
        pass

    return False

# ==================== 创建主窗口 ====================
root = tk.Tk()
root.title("Web端自动化测试工具 V1.0")
root.geometry("950x750")
root.resizable(False, False)
root.configure(bg=BG_COLOR)
root.option_add('*Font', DEFAULT_FONT)

# ==================== 按钮样式配置 ====================
style = ttk.Style(root)
style.theme_use('clam')
style.configure('Start.TButton', font=BUTTON_FONT, padding=10, background='#3498DB', foreground='white', borderwidth=0)
style.map('Start.TButton', background=[('active','#2980B9'),('disabled','#BDC3C7')], foreground=[('active','white'),('disabled','#7F8C8D')])
style.configure('Stop.TButton', font=BUTTON_FONT, padding=10, background='#E74C3C', foreground='white', borderwidth=0)
style.map('Stop.TButton', background=[('active','#C0392B'),('disabled','#BDC3C7')], foreground=[('active','white'),('disabled','#7F8C8D')])
style.configure('Report.TButton', font=BUTTON_FONT, padding=10, background='#27AE60', foreground='white', borderwidth=0)
style.map('Report.TButton', background=[('active','#1E8449'),('disabled','#BDC3C7')], foreground=[('active','white'),('disabled','#7F8C8D')])

# ==================== 顶部标题区域 ====================
title_frame = tk.Frame(root, bg=BG_COLOR)
title_frame.pack(pady=(20,10))
tk.Label(title_frame, text="🧪", font=("Segoe UI Emoji",24), bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
tk.Label(title_frame, text="Web端自动化测试工具", font=TITLE_FONT, fg=TITLE_COLOR, bg=BG_COLOR).pack(side=tk.LEFT)
tk.Label(title_frame, text="V1.0", font=STATUS_FONT, fg="#7F8C8D", bg=BG_COLOR).pack(side=tk.LEFT, padx=10)

# ==================== 日志显示区域 ====================
log_frame = tk.LabelFrame(root, text=" 执行日志 ", bg=BG_COLOR, fg=TITLE_COLOR, relief=tk.GROOVE, bd=2)
log_frame.pack(padx=25, pady=(10,5), fill=tk.BOTH, expand=True)
log_box = scrolledtext.ScrolledText(log_frame, state=tk.DISABLED, font=LOG_FONT, bg="#1E1E1E", fg="#D4D4D4", wrap=tk.WORD)
log_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# ==================== 按钮区域 ====================
btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(side=tk.BOTTOM, pady=(0,20))

# ==================== 状态栏 ====================
status_bar = tk.Label(root, text="✅ 工具已准备就绪", font=STATUS_FONT, bg=BG_COLOR, fg="#7F8C8D", anchor="w")
status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=(0,10))

# ==================== 全局变量 ====================
is_running = False          # 测试是否正在运行
_test_process = None        # 子进程对象（用于停止测试）

def log(msg):
    """向 GUI 日志区域添加一行消息（线程安全）。"""
    def _update():
        log_box.config(state=tk.NORMAL)
        log_box.insert(tk.END, f"{msg}\n")
        log_box.see(tk.END)
        log_box.config(state=tk.DISABLED)
    root.after(0, _update)

def set_buttons_state(enable_2d, enable_3d, enable_stop):
    """启用/禁用开始2D、开始3D、停止按钮。"""
    def _set():
        btn2d.config(state=tk.NORMAL if enable_2d else tk.DISABLED)
        btn3d.config(state=tk.NORMAL if enable_3d else tk.DISABLED)
        btnStop.config(state=tk.NORMAL if enable_stop else tk.DISABLED)
    root.after(0, _set)

def kill_process():
    """终止正在运行的测试进程（如果存在）。"""
    global is_running, _test_process
    if is_running:
        if _test_process and _test_process.poll() is None:
            _test_process.terminate()
            try:
                _test_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                _test_process.kill()
        is_running = False
        set_buttons_state(True, True, False)
        log("\n🛑 测试已停止")

def open_report():
    """打开最新的 HTML 测试报告（位于 report/ 目录下）。"""
    report_dir = os.path.join(os.path.abspath("."), "report")
    if not os.path.isdir(report_dir):
        messagebox.showwarning("提示", "report 文件夹不存在，请先运行测试。")
        return
    files = [f for f in os.listdir(report_dir) if f.startswith("report_") and f.endswith(".html")]
    if not files:
        messagebox.showwarning("提示", "未找到任何测试报告，请先运行测试。")
        return
    latest = max(files, key=lambda x: os.path.getmtime(os.path.join(report_dir, x)))
    os.startfile(os.path.join(report_dir, latest))

def run_auto(env):
    """
    启动测试（根据是否打包选择不同方式）。
    :param env: "2d" 或 "3d" 环境
    """
    global is_running, _test_process
    if is_running:
        return

    if not is_chrome_installed():
        log("❌ 未检测到Chrome浏览器")
        messagebox.showerror("错误", "未检测到Chrome浏览器")
        return

    set_buttons_state(False, False, True)
    is_running = True
    log("=" * 80)
    log(f"▶ 开始【{env}】环境测试")
    log("=" * 80)
    log("🔄 正在准备测试环境（首次运行会自动下载 ChromeDriver，请稍候）...")

    def target():
        global is_running, _test_process
        try:
            if getattr(sys, 'frozen', False):
                # 打包后：启动自身子进程，并传递 --run-test 参数
                exe_path = sys.executable
                cmd = [exe_path, "--run-test", env]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                _test_process = process
                for line in iter(process.stdout.readline, ''):
                    if line:
                        log(line.rstrip())
                process.wait()
                if process.returncode != 0:
                    log("❌ 测试执行失败")
                else:
                    log("\n✅ 测试执行完成！")
            else:
                # 开发环境：直接调用 run_tests（使用 direct_mode 避免嵌套子进程）
                result = run.run_tests(env, log_callback=log, direct_mode=True)
                if result is None:
                    log("❌ 测试执行失败")
                else:
                    log("\n✅ 测试执行完成！")
        except Exception as e:
            log(f"❌ 错误：{e}")
        finally:
            is_running = False
            _test_process = None
            set_buttons_state(True, True, False)

    threading.Thread(target=target, daemon=True).start()

def on_closing():
    """窗口关闭时的回调函数：如果测试正在运行，询问用户是否确认退出。"""
    if is_running:
        if messagebox.askyesno("确认", "测试正在运行，确定退出？"):
            kill_process()
            root.destroy()
    else:
        root.destroy()

# ==================== 创建按钮（保留原有表情符号） ====================
btn2d = ttk.Button(btn_frame, text="🚀 开始2D测试", style="Start.TButton", width=18,
                   command=lambda: threading.Thread(target=run_auto, args=("2d",), daemon=True).start())
btn3d = ttk.Button(btn_frame, text="🚀 开始3D测试", style="Start.TButton", width=18,
                   command=lambda: threading.Thread(target=run_auto, args=("3d",), daemon=True).start())
btnStop = ttk.Button(btn_frame, text="🛑 停止测试", style="Stop.TButton", width=16, state=tk.DISABLED,
                     command=kill_process)
btnReport = ttk.Button(btn_frame, text="📄 打开报告", style="Report.TButton", width=16,
                       command=open_report)

# 网格布局
btn2d.grid(row=0, column=0, padx=12, pady=5)
btn3d.grid(row=0, column=1, padx=12, pady=5)
btnStop.grid(row=0, column=2, padx=12, pady=5)
btnReport.grid(row=0, column=3, padx=12, pady=5)

# 启动时的提示信息
log("✅ 工具已准备就绪")
log("⚡ 首次运行测试时，将会自动下载匹配的 ChromeDriver（需联网），请耐心等待...")
log("📌 所有报告将统一生成在 report/ 文件夹（每次运行只保留最新报告）")

# 绑定窗口关闭事件
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()