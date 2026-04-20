import unittest
import time
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from pages.map_page import MapPage
from pages.route_page import RoutePage
from pages.task_page import TaskPage

@allure.feature("业务流程自动化测试")
@allure.severity("critical")
class TestBusinessFlow(unittest.TestCase):
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

            print("正在自动匹配 ChromeDriver（Selenium Manager）...")
            cls.driver = webdriver.Chrome(options=chrome_options)
            
            cls.driver.maximize_window()
            cls.driver.implicitly_wait(10)

            cls.login_page = LoginPage(cls.driver)
            cls.map_page = MapPage(cls.driver)
            cls.route_page = RoutePage(cls.driver)
            cls.task_page = TaskPage(cls.driver)

            print("正在登录系统...")
            cls.login_page.login()
            print("✅ 初始化完成，浏览器正常打开！")

        except Exception as e:
            print(f"❌ 初始化失败：{str(e)}")
            raise

    @classmethod
    def tearDownClass(cls):
        # ===================== 修复 5：浏览器关闭防崩溃 =====================
        try:
            time.sleep(2)
            cls.driver.delete_all_cookies()
            time.sleep(1)
            cls.driver.quit()
            print("\n测试结束，浏览器已关闭")
        except:
            pass

    # ===================== 修复 2：失败自动截图（现在必生效） =====================
    def tearDown(self):
        if not self._outcome.success:
            try:
                png = self.driver.get_screenshot_as_png()
                allure.attach(
                    png,
                    name=f"失败截图_{self._testMethodName}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"截图失败：{e}")

    # ===================== 用例（编号 1-20 连续，无共享变量） =====================
    @allure.title("1. 取消创建地图")
    def test_01_cancel_create_map(self):
        self.map_page.cancel_create_map()

    @allure.title("2. 创建新地图")
    def test_02_create_new_map(self):
        # ===================== 修复 1：删除共享变量 self.map_name =====================
        self.map_page.create_new_map()

    @allure.title("3. 编辑地图")
    def test_03_edit_map(self):
        map_index = self.map_page.get_map_count()
        self.map_page.edit_map(map_index)

    @allure.title("4. 扩展地图")
    def test_04_expand_map(self):
        map_index = self.map_page.get_map_count()
        self.map_page.expand_map(map_index)

    @allure.title("5. 删除地图")
    def test_05_delete_map(self):
        map_index = self.map_page.get_map_count()
        self.map_page.delete_map(map_index)

    @allure.title("6. 上传地图")
    def test_06_upload_map(self):
        self.map_page.upload_map()

    @allure.title("7. 设置最后一个地图为默认")
    def test_07_set_last_map_default(self):
        self.map_page.set_last_map_default()

    @allure.title("8. 再次删除地图")
    def test_08_delete_map_again(self):
        map_index = self.map_page.get_map_count() - 1
        self.map_page.delete_map(map_index)

    @allure.title("9. 重新定位")
    def test_09_relocate(self):
        self.map_page.relocate()

    @allure.title("10. 创建教学路线")
    def test_10_create_teach_route(self):
        self.route_page.create_teach_route()

    @allure.title("11. 创建普通路线")
    def test_11_create_normal_route(self):
        self.route_page.create_normal_route()

    @allure.title("12. 创建填充路线")
    def test_12_create_fillin_route(self):
        self.route_page.create_fillin_route()

    @allure.title("13. 编辑路线")
    def test_13_edit_route(self):
        self.route_page.edit_route()

    @allure.title("14. 删除路线")
    def test_14_delete_route(self):
        # ===================== 修复 3：删除路线 BUG =====================
        route_index = self.route_page.get_route_count()
        self.route_page.delete_route(route_index)

    @allure.title("15. 创建新任务")
    def test_15_create_new_task(self):
        self.task_page.create_new_task()

    @allure.title("16. 编辑任务")
    def test_16_edit_task(self):
        self.task_page.edit_task()

    @allure.title("17. 删除任务")
    def test_17_delete_task(self):
        self.task_page.delete_task()

    @allure.title("18. 进入地图管理页面")
    def test_18_enter_map_page(self):
        self.map_page.enter_map_page()

    @allure.title("19. 设置第一个地图为默认")
    def test_19_set_first_map_default(self):
        self.map_page.set_first_map_default()

    @allure.title("20. 删除最后一个地图")
    def test_20_delete_last_map(self):
        self.map_page.delete_last_map()

if __name__ == '__main__':
    unittest.main(verbosity=2)