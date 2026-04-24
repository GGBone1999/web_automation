import os
import sys
import time
import subprocess
import xml.etree.ElementTree as ET
from feishu_notice import send_feishu_report

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_env_from_args_or_interactive():
    """优先命令行参数，若无则交互式选择"""
    if len(sys.argv) > 1:
        env = sys.argv[1].lower()
        if env in ["2d", "3d"]:
            return env
        else:
            print(f"⚠️ 环境参数错误：{env}，仅支持2d/3d，将使用交互式选择")
    
    while True:
        choice = input("请选择雷达类型 [2d/3d] (默认2d): ").strip().lower()
        if choice in ["2d", "3d"]:
            return choice
        elif choice == "":
            return "2d"
        else:
            print("输入无效，请输入 2d 或 3d")

def run_tests_and_get_stats(test_dir="cases", junit_file="test_results.xml", output_log="pytest_output.log", env="2d"):
    # 确保日志目录存在
    log_dir = os.path.dirname(output_log)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 注意：不再传递 --env 参数，因为会导致 pytest 报错
    cmd = [
        "pytest", test_dir,
        f"--junitxml={junit_file}",
        "-v", "-s", "--tb=short"
    ]

    # 设置环境变量
    env_dict = os.environ.copy()
    env_dict["PYTHONIOENCODING"] = "utf-8"
    env_dict["PYTHONUTF8"] = "1"
    env_dict["TEST_ENV_TYPE"] = env          # 通过环境变量传递环境
    project_root = os.path.dirname(os.path.abspath(__file__))
    if "PYTHONPATH" in env_dict:
        env_dict["PYTHONPATH"] = project_root + os.pathsep + env_dict["PYTHONPATH"]
    else:
        env_dict["PYTHONPATH"] = project_root

    timeout_seconds = 900  # 15分钟

    # 执行 pytest
    try:
        with open(output_log, "wb") as log_f:
            result = subprocess.run(
                cmd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
                text=False,
                env=env_dict,
                timeout=timeout_seconds
            )
        # 打印日志到控制台（实时输出）
        with open(output_log, "r", encoding="utf-8", errors="replace") as log_f:
            for line in log_f:
                try:
                    print(line, end="")
                except UnicodeEncodeError:
                    safe_line = line.encode('ascii', errors='replace').decode('ascii')
                    print(safe_line, end="")
    except subprocess.TimeoutExpired as e:
        error_msg = f"测试执行超时（{timeout_seconds}秒）\n"
        print(error_msg)
        with open(output_log, "a", encoding="utf-8") as log_f:
            log_f.write(error_msg)
        return 0, 0, 1, 0
    except Exception as e:
        print(f"运行测试失败: {e}")
        return 0, 0, 1, 0

    # 等待 JUnit 文件生成（增加短暂延迟）
    for _ in range(10):
        if os.path.exists(junit_file):
            break
        time.sleep(0.5)

    # 解析 JUnit XML
    if not os.path.exists(junit_file):
        print(f"⚠️ JUnit 报告文件未生成: {junit_file}")
        return 0, 0, 1, 0

    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()
        testsuite = root.find("testsuite")
        if testsuite is None:
            testsuite = root
        total = int(testsuite.get("tests", 0))
        failures = int(testsuite.get("failures", 0))
        errors = int(testsuite.get("errors", 0))
        skipped = int(testsuite.get("skipped", 0))
        passed = total - failures - errors - skipped
        return total, passed, failures + errors, skipped
    except Exception as e:
        print(f"解析 JUnit 报告失败: {e}")
        return 0, 0, 1, 0

if __name__ == "__main__":
    env = get_env_from_args_or_interactive()
    
    print("=" * 50)
    print(f"  UI 自动化测试开始执行（{env.upper()}环境 | 飞书+报告版）")
    print("=" * 50)

    start_time = time.time()
    junit_file = "test_results.xml"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_log = f"reports/logs/pytest_output_{timestamp}_{env}.log"

    result = run_tests_and_get_stats("cases", junit_file, output_log, env)
    if result is None:
        print("❌ 运行测试函数返回 None，使用默认统计值")
        total, passed, failed, skipped = 0, 0, 1, 0
    else:
        total, passed, failed, skipped = result

    duration = f"{round(time.time() - start_time, 2)}s"
    print(f"统计({env.upper()}): 总数={total}, 通过={passed}, 失败={failed}, 跳过={skipped}, 耗时={duration}")

    try:
        send_feishu_report(total, passed, failed, skipped, duration)
    except Exception as e:
        print(f"飞书通知发送失败: {e}")

    if os.path.exists(junit_file):
        try:
            os.remove(junit_file)
            print(f"已删除临时文件: {junit_file}")
        except Exception as e:
            print(f"删除临时文件失败: {e}")

    print("\n全部完成!")
    print(f"pytest 输出日志: {output_log}")
    sys.exit(0)