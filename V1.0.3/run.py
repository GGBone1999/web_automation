# -*- coding: utf-8 -*-
"""
自动化测试执行模块

本模块负责：
- 根据环境（2D/3D）启动 pytest 并执行测试用例
- 支持开发模式（子进程）和打包后模式（直接调用 pytest.main）
- 生成简洁的 HTML 测试报告（不依赖 pytest-html）
- 发送测试结果到飞书群
- 自动清理临时文件（JUnit XML、pytest 日志）
"""

import os
import sys
import time
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime

# 将当前目录添加到 Python 路径，方便导入项目内部模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 全局变量：当前运行的 pytest 子进程（仅用于开发模式下停止测试）
_current_process = None


def stop_test():
    """终止当前正在运行的测试子进程（开发模式）"""
    global _current_process
    if _current_process and _current_process.poll() is None:
        _current_process.terminate()
        try:
            _current_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _current_process.kill()
    _current_process = None


# ==================== 飞书通知（无表情符号，避免编码错误） ====================
def send_feishu_notification(env, total, passed, failed, skipped, duration, log_func):
    """
    发送测试报告到飞书群。

    :param env: 测试环境标识（"2d" / "3d"）
    :param total: 总用例数
    :param passed: 通过数
    :param failed: 失败/错误数
    :param skipped: 跳过数
    :param duration: 执行耗时（字符串）
    :param log_func: 日志回调函数，用于输出发送结果（例如 print 或 GUI 的 log）
    """
    try:
        import requests
        WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/89697790-6cdb-41b0-88f0-8be669d13257"
        content = f"""
UI自动化测试完成
环境：{env.upper()}
用例总数：{total}
通过：{passed}
失败：{failed}
跳过：{skipped}
耗时：{duration}
"""
        data = {"msg_type": "text", "content": {"text": content}}
        resp = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            log_func("飞书报告已发送")
        else:
            log_func(f"飞书通知返回异常: {resp.text}")
    except Exception as e:
        log_func(f"飞书通知发送失败: {e}")


# ==================== HTML 报告生成（不使用 pytest-html，避免依赖缺失） ====================
def generate_simple_html_report(junit_file, html_file, env):
    """
    从 JUnit XML 文件生成简易 HTML 测试报告。

    :param junit_file: JUnit XML 文件路径
    :param html_file: 输出的 HTML 文件路径
    :param env: 环境标识（用于报告标题）
    :return: 元组 (total, passed, failed, skipped, duration) 或 None（失败时）
    """
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()
        testsuite = root.find("testsuite") or root
        total = int(testsuite.get("tests", 0))
        failures = int(testsuite.get("failures", 0))
        errors = int(testsuite.get("errors", 0))
        skipped = int(testsuite.get("skipped", 0))
        passed = total - failures - errors - skipped
        duration = testsuite.get("time", "0")
        timestamp = testsuite.get("timestamp", datetime.now().isoformat())

        test_cases = []
        for testcase in testsuite.findall("testcase"):
            name = testcase.get("name", "")
            classname = testcase.get("classname", "")
            time_val = testcase.get("time", "0")
            status = "passed"
            message = ""
            failure = testcase.find("failure")
            error = testcase.find("error")
            skipped_elem = testcase.find("skipped")
            if failure is not None:
                status = "failed"
                message = failure.get("message", "Failure")
            elif error is not None:
                status = "error"
                message = error.get("message", "Error")
            elif skipped_elem is not None:
                status = "skipped"
                message = skipped_elem.get("message", "Skipped")
            test_cases.append((classname, name, status, message, time_val))

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>自动化测试报告 - {env.upper()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2C3E50; }}
        .summary {{ margin-bottom: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr.passed {{ background-color: #e8f5e9; }}
        tr.failed {{ background-color: #ffebee; }}
        tr.skipped {{ background-color: #fff3e0; }}
    </style>
</head>
<body>
    <h1>自动化测试报告 - {env.upper()} 环境</h1>
    <div class="summary">
        <p><strong>执行时间：</strong> {timestamp}</p>
        <p><strong>总用例数：</strong> {total}</p>
        <p><strong><span class="passed">通过：</span></strong> {passed}</p>
        <p><strong><span class="failed">失败/错误：</span></strong> {failures + errors}</p>
        <p><strong><span class="skipped">跳过：</span></strong> {skipped}</p>
        <p><strong>耗时：</strong> {duration} 秒</p>
    </div>
    <h2>用例详情</h2>
    <table>
        <thead>
            <tr><th>类名</th><th>用例名</th><th>状态</th><th>信息</th><th>耗时(s)</th></tr>
        </thead>
        <tbody>
"""
        for classname, name, status, message, time_val in test_cases:
            status_class = status
            # 状态显示用纯文本，避免 emoji 在控制台乱码
            status_display = {"passed":"PASS", "failed":"FAIL", "error":"ERROR", "skipped":"SKIP"}.get(status, status)
            # 【修复】：删除多余的<tr>标签，确保表格行与表头列数一致（原错误：多写一个<tr>导致列错位）
            html += f'<tr class="{status_class}"><td>{classname}</td><td>{name}</td><td>{status_display}</td><td>{message}</td><td>{time_val}</td></tr>\n'
        html += """
        </tbody>
    </table>
</body>
</html>"""
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        return (total, passed, failures + errors, skipped, duration)
    except Exception as e:
        print(f"生成 HTML 报告失败: {e}")
        return None


# ==================== 主测试函数 ====================
def run_tests(env, log_callback=None, direct_mode=False):
    """
    执行自动化测试的主函数。

    :param env: 环境类型 "2d" 或 "3d"
    :param log_callback: 可选的日志回调函数，接收字符串参数（用于 GUI 实时显示）
    :param direct_mode: True=在当前进程中调用 pytest.main（用于打包后子进程模式）；
                        False=启动独立子进程运行 pytest（开发模式）
    :return: 元组 (total, passed, failed, skipped, duration) 或 None（失败时）
    """
    def log(msg):
        """内部日志输出：优先使用回调，否则打印到终端（处理编码异常）"""
        if log_callback:
            try:
                log_callback(msg)
            except Exception:
                pass
        else:
            try:
                print(msg)
            except UnicodeEncodeError:
                print(msg.encode('gbk', errors='ignore').decode('gbk'))

    start_time = time.time()
    log("=" * 50)
    log(f"正在运行：{env.upper()} 环境自动化测试")
    log("=" * 50)

    # 创建报告目录和驱动缓存目录
    output_dir = "report"
    os.makedirs(output_dir, exist_ok=True)

    cache_dir = os.path.join(os.path.abspath("."), "drivers_cache")
    os.makedirs(cache_dir, exist_ok=True)

    # 生成带时间戳的临时文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    junit_file = os.path.join(output_dir, f"test_results_{timestamp}.xml").replace("\\", "/")
    html_report = os.path.join(output_dir, f"report_{env}_{timestamp}.html").replace("\\", "/")
    output_log = os.path.join(output_dir, f"pytest_output_{timestamp}_{env}.log").replace("\\", "/")

    # 构建子进程的环境变量（包括编码、测试类型、缓存路径等）
    env_dict = os.environ.copy()
    env_dict["PYTHONIOENCODING"] = "utf-8"
    env_dict["PYTHONUTF8"] = "1"
    env_dict["TEST_ENV_TYPE"] = env
    env_dict["PYTHONPATH"] = os.path.abspath(".") + os.pathsep + env_dict.get("PYTHONPATH", "")
    env_dict["SELENIUM_DRIVER_CACHE_PATH"] = cache_dir
    env_dict["WDM_CACHE_PATH"] = cache_dir

    if direct_mode:
        # ========== 直接模式（打包后使用） ==========
        import pytest

        # 模拟 allure 模块，避免因缺少 allure 导致测试用例导入失败
        if 'allure' not in sys.modules:
            class AllureMock:
                def __getattr__(self, name):
                    def identity_decorator(*args, **kwargs):
                        def decorator(func):
                            return func
                        return decorator
                    return identity_decorator
                def __call__(self, *args, **kwargs):
                    pass
            sys.modules['allure'] = AllureMock()

        # 确定测试用例目录：打包后从 _MEIPASS 中读取，开发环境直接使用 "cases"
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            test_dir = os.path.join(base_path, "cases")
            if base_path not in sys.path:
                sys.path.insert(0, base_path)
        else:
            test_dir = "cases"

        if not os.path.isdir(test_dir):
            log(f"找不到测试用例目录：{test_dir}")
            return None

        # pytest 命令行参数（禁用可能冲突的插件）
        args = [
            "-c", "nul",                # 忽略任何 pytest.ini 配置文件
            test_dir,
            f"--junitxml={junit_file}",
            "-v", "-s", "--tb=short",
            "-p", "no:cacheprovider",   # 禁用缓存插件
            "-p", "no:allure",          # 禁用 allure 插件
            "-p", "no:allure_pytest",
            "--capture=no",             # 完全关闭输出捕获
        ]

        # 临时清除环境变量 PYTEST_ADDOPTS，避免外部参数干扰
        old_addopts = os.environ.pop("PYTEST_ADDOPTS", None)
        env_dict["PYTEST_ADDOPTS"] = ""
        for k, v in env_dict.items():
            os.environ[k] = v

        # 将 pytest 输出重定向到临时文件，避免阻塞 GUI
        tmp_out = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False, suffix='.log')
        tmp_out.close()

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        with open(tmp_out.name, 'w', encoding='utf-8') as f:
            sys.stdout = f
            sys.stderr = f
            try:
                retcode = pytest.main(args)
            except Exception as e:
                log(f"pytest.main 异常: {e}")
                retcode = 1
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

        # 恢复环境变量
        if old_addopts is not None:
            os.environ["PYTEST_ADDOPTS"] = old_addopts
        else:
            os.environ.pop("PYTEST_ADDOPTS", None)

        # 将临时文件中的 pytest 输出逐行打印到日志
        try:
            with open(tmp_out.name, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        log(line.rstrip())
        finally:
            os.unlink(tmp_out.name)

        if retcode != 0:
            log(f"pytest 返回码：{retcode}")

        # 生成 HTML 报告并删除临时 XML 文件
        stats = None
        if os.path.exists(junit_file):
            stats = generate_simple_html_report(junit_file, html_report, env)
            if stats:
                log(f"已生成 HTML 报告：{html_report}")
                try:
                    os.unlink(junit_file)
                    log("已删除临时 XML 文件")
                except Exception:
                    pass
            else:
                log("生成 HTML 报告失败")
        else:
            log("未生成 JUnit 报告")

        # 删除 pytest 输出日志（可选项）
        try:
            if os.path.exists(output_log):
                os.unlink(output_log)
        except Exception:
            pass

        # 提取统计数据
        if stats:
            total, passed, failed, skipped, exec_duration = stats
        else:
            total = passed = failed = skipped = 0
            exec_duration = "0s"

        duration = exec_duration if exec_duration != "0s" else f"{round(time.time() - start_time, 2)}s"
        log(f"\n执行结果：总数={total} 成功={passed} 失败={failed} 跳过={skipped} 耗时={duration}")

        # 发送飞书通知（发送失败不影响测试结果）
        send_feishu_notification(env, total, passed, failed, skipped, duration, log)

        # 直接返回结果，避免走到下方的通用解析
        return total, passed, failed, skipped, duration

    else:
        # ========== 开发模式：通过子进程运行 pytest ==========
        cmd = [
            sys.executable, "-m", "pytest", "cases",
            f"--junitxml={junit_file}",
            f"--html={html_report}", "--self-contained-html",
            "-v", "-s", "--tb=short"
        ]
        timeout_seconds = 900
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env_dict,
                creationflags=creation_flags
            )
            global _current_process
            _current_process = process

            # 实时读取子进程输出并写入日志文件
            with open(output_log, "w", encoding="utf-8", errors="replace") as log_f:
                for line in iter(process.stdout.readline, ""):
                    if line:
                        log(line.rstrip())
                        log_f.write(line)

            process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            log(f"测试执行超时（{timeout_seconds}秒）")
            return None
        except Exception as e:
            log(f"运行测试失败: {e}")
            return None
        finally:
            _current_process = None

        # 解析 JUnit 报告获取统计信息
        if not os.path.exists(junit_file):
            log("JUnit 报告文件未生成")
            return None

        try:
            tree = ET.parse(junit_file)
            root = tree.getroot()
            testsuite = root.find("testsuite") or root
            total = int(testsuite.get("tests", 0))
            failures = int(testsuite.get("failures", 0))
            errors = int(testsuite.get("errors", 0))
            skipped = int(testsuite.get("skipped", 0))
            passed = total - failures - errors - skipped
        except Exception as e:
            log(f"解析 JUnit 报告失败: {e}")
            return None

        duration = f"{round(time.time() - start_time, 2)}s"
        log(f"\n执行结果：总数={total} 成功={passed} 失败={failures+errors} 跳过={skipped} 耗时={duration}")

        # 发送飞书通知
        send_feishu_notification(env, total, passed, failures+errors, skipped, duration, log)

        # 清理中间文件（JUnit XML 和 pytest 日志）
        try:
            if os.path.exists(junit_file):
                os.unlink(junit_file)
            if os.path.exists(output_log):
                os.unlink(output_log)
        except Exception:
            pass

        return total, passed, failures+errors, skipped, duration


if __name__ == "__main__":
    """
    命令行独立运行入口（用于调试）。
    支持通过第一个参数直接指定环境（2d/3d），否则交互式选择。
    """
    if len(sys.argv) > 1:
        env = sys.argv[1].lower()
        if env not in ["2d", "3d"]:
            print(f"环境参数错误：{env}，将使用交互式选择")
            env = None
    else:
        env = None

    if env is None:
        print("=" * 50)
        print("        雷达自动化测试工具")
        print("=" * 50)
        while True:
            choice = input("请选择雷达类型 [2d/3d] (默认2d): ").strip().lower()
            if choice in ["2d", "3d"]:
                env = choice
                break
            elif choice == "":
                env = "2d"
                break
            print("输入错误，请输入 2d 或 3d！")

    run_tests(env, log_callback=print, direct_mode=False)