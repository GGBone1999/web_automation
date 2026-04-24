from base.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

class LoginPage(BasePage):
    """登录页元素与操作"""
    
    URL = "http://192.168.5.88:4649/#/login"
    
    # 登录相关定位
    INPUT_USERNAME = '//div[contains(@class, "login")]//div[1]/input'
    INPUT_PASSWORD = '//div[contains(@class, "login")]//div[2]/input'
    BTN_SUBMIT = '//div[contains(@class, "login")]//button'
    TEXT_TASK_SETTING = '//div[text()="任务设置"]'
    
    # 弹窗定位
    POPUP_EXCEPTION_RESTART = "//*[text()='异常重启机制']"
    BTN_POPUP_CONFIRM = "//div[contains(@class, 'modal-footer')]//button[1]"

    def __init__(self, driver):
        super().__init__(driver)

    def open_login_page(self):
        self.driver.get(self.URL)
        self.driver.maximize_window()
        # 移除等待，因为后续输入操作会主动等待元素

    def input_login_info(self, username: str, password: str):
        if not username or not password:
            raise ValueError("账号/密码不能为空")
        self.input_xpath(self.INPUT_USERNAME, username)
        self.input_xpath(self.INPUT_PASSWORD, password)

    def click_submit(self):
        self.click_xpath(self.BTN_SUBMIT)

    def handle_exception_restart_popup(self):
        try:
        # 等待弹窗出现，最多 1 秒
            WebDriverWait(self.driver, 1).until(
                EC.visibility_of_element_located((By.XPATH, self.POPUP_EXCEPTION_RESTART))
            )
            print("⚠️ 检测到异常重启弹窗，正在关闭")
            # 点击关闭按钮，使用较短超时
            if self.click_xpath(self.BTN_POPUP_CONFIRM, wait_time=2):
                print("✅ 异常重启弹窗已关闭")
            else:
                print("⚠️ 弹窗按钮点击失败，已跳过")
        except TimeoutException:
            print("✅ 无异常重启弹窗")
        except Exception as e:
            print(f"⚠️ 处理弹窗失败: {e}")

    def login(self, username: str = "superadmin", password: str = "Super678@!~"):
        """登录流程，带耗时打印（可删除打印）"""
        t0 = time.time()
        
        self.open_login_page()
        print(f"打开登录页耗时: {time.time()-t0:.2f}s")
        
        t1 = time.time()
        self.input_login_info(username, password)
        print(f"输入账号密码耗时: {time.time()-t1:.2f}s")
        
        t2 = time.time()
        self.click_submit()
        print(f"点击登录按钮耗时: {time.time()-t2:.2f}s")
        
        t3 = time.time()
        self.handle_exception_restart_popup()
        print(f"处理弹窗耗时: {time.time()-t3:.2f}s")
        
        t4 = time.time()
        self.wait_xpath(self.TEXT_TASK_SETTING, timeout=15)
        print(f"等待任务设置元素耗时: {time.time()-t4:.2f}s")
        
        print(f"登录总耗时: {time.time()-t0:.2f}s")
        print("✅ 登录成功")
        return True