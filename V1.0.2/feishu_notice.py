import requests
import json

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/89697790-6cdb-41b0-88f0-8be669d13257"

def send_feishu_report(total=0, passed=0, failed=0, skipped=0, duration="0s"):
    content = f"""
🔵 UI自动化测试完成
用例总数：{total}
通过：{passed}
失败：{failed}
跳过：{skipped}
耗时：{duration}
"""

    data = {
        "msg_type": "text",
        "content": {"text": content}
    }

    try:
        res = requests.post(WEBHOOK_URL, json=data, timeout=10)
        print("✅ 飞书通知发送成功：", res.json())
    except Exception as e:
        print("❌ 飞书发送失败：", e)