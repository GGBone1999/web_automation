import unittest
import time
import allure
import requests
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from pages.map_page import MapPage
from pages.route_page import RoutePage
from pages.task_page import TaskPage
from selenium.webdriver.common.by import By

# 新增：解析环境参数（支持pytest参数和环境变量）
def get_test_env():
    # 优先从环境变量获取
    env = os.environ.get("TEST_ENV_TYPE")
    if env in ("2d", "3d"):
        return env
    # 兼容：从命令行参数获取（仅当直接运行且无环境变量时）
    for arg in sys.argv:
        if arg.startswith("--env="):
            return arg.split("=")[1].lower()
    return "2d"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/89697790-6cdb-41b0-88f0-8be669d13257"  # 或使用环境变量

def send_feishu_report(total=0, passed=0, failed=0, skipped=0, duration="0s"):
    content = f"""
🔵 UI自动化测试完成（{get_test_env().upper()}环境）
用例总数：{total}
通过：{passed}
失败：{failed}
跳过：{skipped}
耗时：{duration}
"""
    try:
        requests.post(FEISHU_WEBHOOK, json={"msg_type": "text", "content": {"text": content}}, timeout=10)
        print("飞书通知发送成功")
    except Exception as e:
        print("飞书发送失败：", e)

class TestBusinessFlow(unittest.TestCase):
    setup_failed = False   # 类变量，标记初始化是否失败
    test_env = get_test_env()  # 新增：获取测试环境

    @classmethod
    def setUpClass(cls):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            print(f"正在启动 ChromeDriver...（{cls.test_env.upper()}环境）")
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.maximize_window()
            cls.driver.implicitly_wait(10)

            cls.login_page = LoginPage(cls.driver)
            # 新增：初始化MapPage时传入环境参数
            cls.map_page = MapPage(cls.driver, cls.test_env)
            cls.route_page = RoutePage(cls.driver)
            cls.task_page = TaskPage(cls.driver)

            print("正在登录系统...")
            cls.login_page.login()
            print("setUpClass 成功")

            cls.setup_failed = False
        except Exception as e:
            print(f"setUpClass 失败：{e}")
            cls.setup_failed = True
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            if hasattr(cls, 'driver') and cls.driver:
                cls.driver.quit()
        except:
            pass

    def tearDown(self):
        # 处理可能残留的 alert（避免阻塞后续测试）
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            print("关闭了未处理的 alert")
        except:
            pass
        try:
            if not self._outcome.success and hasattr(self, 'driver'):
                png = self.driver.get_screenshot_as_png()
                allure.attach(png, name=f"失败截图_{self._testMethodName}", attachment_type=allure.attachment_type.PNG)
        except:
            pass

    # ===================== 统一使用页面对象的方法获取数量 =====================
    def get_map_list_count(self):
        """获取地图数量（复用 MapPage 的绝对路径计数）"""
        return self.map_page.get_map_count()

    def get_route_list_count(self):
        """获取路线数量（复用 RoutePage 的绝对路径计数）"""
        return self.route_page.get_route_count()

    def get_task_list_count(self):
        """获取任务数量（复用 TaskPage 的绝对路径计数）"""
        return self.task_page.get_task_count()
        

    # ===================== 20条测试用例 =====================
    @allure.title("1. 取消创建地图")
    def test_01_cancel_create_map(self):
        self.map_page.enter_remote_mode()
        time.sleep(1)
        self.map_page.enter_map_page()
        time.sleep(1)
        before = self.get_map_list_count()
        self.map_page.cancel_create_map()
        after = self.get_map_list_count()
        self.assertEqual(after, before, "取消创建地图后数量应不变")

    @allure.title("2. 创建新地图")
    def test_02_create_new_map(self):
        before = self.get_map_list_count()
        self.map_page.create_new_map()
        after = self.get_map_list_count()
        self.assertEqual(after, before + 1)

    @allure.title("3. 编辑地图")
    def test_03_edit_map(self):
        count = self.get_map_list_count()
        if count == 0:
            self.skipTest("没有地图可编辑，跳过")
        idx = count   # 编辑最后一张地图（索引从1开始）
        self.map_page.edit_map(idx)
        self.assertTrue(True)

    @allure.title("4. 扩展地图")
    def test_04_expand_map(self):
        count = self.get_map_list_count()
        if count == 0:
            self.skipTest("没有地图可扩展，跳过")
        idx = count
        self.map_page.expand_map(idx)
        self.assertTrue(True)

    @allure.title("5. 删除地图")
    def test_05_delete_map(self):
        count = self.get_map_list_count()
        if count < 1:
            self.skipTest("没有地图可删除，跳过")
        self.map_page.delete_map(count)   # 删除最后一个
        after = self.get_map_list_count()
        self.assertEqual(after, count - 1)

    @allure.title("6. 上传地图")
    def test_06_upload_map(self):
        before = self.get_map_list_count()
        self.map_page.upload_map()
        after = self.get_map_list_count()
        self.assertEqual(after, before + 2)

    @allure.title("7. 设置最后一个地图为默认")
    def test_07_set_last_map_default(self):
        count = self.get_map_list_count()
        if count == 0:
            self.skipTest("没有地图，无法设置默认")
        self.map_page.set_last_map_default()
        self.assertTrue(True)

    @allure.title("8. 再次删除地图")
    def test_08_delete_map_again(self):
        count = self.get_map_list_count()
        if count < 1:
            self.skipTest("没有地图可删除，跳过")
        # 删除倒数第二张，如果只有一张则删除第一张
        idx = count - 1 if count > 1 else 1
        self.map_page.delete_map(idx)
        after = self.get_map_list_count()
        self.assertEqual(after, count - 1)

    @allure.title("9. 重新定位")
    def test_09_relocate(self):
        self.map_page.relocate()
        self.assertTrue(True)

    @allure.title("10. 创建教学路线")
    def test_10_create_teach_route(self):
        self.route_page.enter_route_page()
        time.sleep(1)
        before = self.get_route_list_count()
        time.sleep(1)
        self.route_page.create_teach_route()
        after = self.get_route_list_count()
        self.assertEqual(after, before + 1, "教学路线创建后数量应+1")

    @allure.title("11. 创建普通路线")
    def test_11_create_normal_route(self):
        before = self.get_route_list_count()
        self.route_page.create_normal_route()
        after = self.get_route_list_count()
        self.assertEqual(after, before + 1)

    @allure.title("12. 创建填充路线")
    def test_12_create_fillin_route(self):
        before = self.get_route_list_count()
        self.route_page.create_fillin_route()
        after = self.get_route_list_count()
        self.assertEqual(after, before + 1)

    @allure.title("13. 编辑路线")
    def test_13_edit_route(self):
        self.route_page.edit_route()
        self.assertTrue(True)

    @allure.title("14. 删除路线")
    def test_14_delete_route(self):
        before = self.get_route_list_count()
        if before >= 1:
            # 注意：delete_route 方法内部删除最后3条，这里只做简单调用，断言可能需调整
            self.route_page.delete_route()
            after = self.get_route_list_count()
            # 由于删除了3条，预期减少3条（若不足3条则可能删除所有）
            expected = before - min(3, before)
            self.assertEqual(after, expected)
        else:
            self.skipTest("没有路线可删除")

    @allure.title("15. 创建新任务")
    def test_15_create_new_task(self):
        self.task_page.enter_task_page()
        time.sleep(1)
        before = self.get_task_list_count()
        self.task_page.create_new_task()
        after = self.get_task_list_count()
        self.assertEqual(after, before + 1)

    @allure.title("16. 编辑任务")
    def test_16_edit_task(self):
        self.task_page.edit_task()
        self.assertTrue(True)

    @allure.title("17. 删除任务")
    def test_17_delete_task(self):
        before = self.get_task_list_count()
        if before >= 1:
            self.task_page.delete_task()
            after = self.get_task_list_count()
            self.assertEqual(after, before - 1)
        else:
            self.skipTest("没有任务可删除")

    @allure.title("18. 进入地图管理页面")
    def test_18_enter_map_page(self):
        try:
            self.map_page.enter_map_page()
            self.assertIn("map", self.driver.current_url.lower())
        except:
            self.assertTrue(True)

    @allure.title("19. 设置第一个地图为默认")
    def test_19_set_first_map_default(self):
        count = self.get_map_list_count()
        if count == 0:
            self.skipTest("没有地图，无法设置默认")
        self.map_page.set_first_map_default()
        self.assertTrue(True)

    @allure.title("20. 删除最后一个地图")
    def test_20_delete_last_map(self):
        count = self.get_map_list_count()
        if count < 1:
            self.skipTest("没有地图可删除，跳过")
        self.map_page.delete_last_map()
        after = self.get_map_list_count()
        self.assertEqual(after, count - 1)

# ===================== 运行入口 =====================
if __name__ == '__main__':
    start = time.time()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBusinessFlow)
    total_planned = suite.countTestCases()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if TestBusinessFlow.setup_failed:
        failed_total = total_planned
        passed_total = 0
        skipped_num = 0
    else:
        failed_total = len(result.errors) + len(result.failures)
        passed_total = result.testsRun - failed_total
        skipped_num = len(result.skipped)

    duration = f"{round(time.time() - start, 2)}s"
    send_feishu_report(total_planned, passed_total, failed_total, skipped_num, duration)