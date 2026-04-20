import pytest
import os
import sys
import time
from feishu_notice import send_feishu_report

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 50)
    print("  UI 自动化测试开始执行（飞书+报告版）")
    print("=" * 50)

    start_time = time.time()

    result_dir = "./allure-results"
    html_report = "./report/result.html"

    if os.path.exists(result_dir):
        import shutil
        shutil.rmtree(result_dir)

    exit_code = pytest.main([
        "-v",
        "-s",
        "--tb=short",
        "cases/",
        f"--html={html_report}",
        "--self-contained-html",
        "--alluredir", result_dir,
        "--capture=no"
    ])

    duration = f"{round(time.time() - start_time, 2)}s"

    total = 19
    failed = exit_code
    passed = total - failed
    skipped = 0

    send_feishu_report(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration=duration
    )

    print("\n✅ 全部完成！")
    print(f"📄 HTML 报告：{html_report}")