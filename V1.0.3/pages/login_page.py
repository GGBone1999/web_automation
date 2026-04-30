# -*- coding: utf-8 -*-
"""
登录页面对象模块

封装登录页面的元素定位、操作流程及异常弹窗处理。
继承自 BasePage，复用基础交互方法。
"""

from base.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time


class LoginPage(BasePage):
    """登录页面对象，提供打开页面、输入账号、点击登录、处理重启弹窗等方法。"""

    URL = "http://192.168.5.88:4649/#/login"

    # ---------- 元素定位 ----------
    INPUT_USERNAME = '//div[contains(@class, "login")]//div[1]/input'   # 用户名输入框
    INPUT_PASSWORD = '//div[contains(@class, "login")]//div[2]/input'   # 密码输入框
    BTN_SUBMIT = '//div[contains(@class, "login")]//button'             # 登录按钮
    TEXT_TASK_SETTING = '//div[text()="任务设置"]'                       # 登录成功后页面上的标识元素

    # ---------- 弹窗定位 ----------
    POPUP_EXCEPTION_RESTART = "//*[text()='异常重启机制']"                # 异常重启弹窗的文本标识
    BTN_POPUP_CONFIRM = "//div[contains(@class, 'modal-footer')]//button[1]"  # 弹窗确认按钮

    def __init__(self, driver):
        """构造函数，调用父类初始化。"""
        super().__init__(driver)

    def open_login_page(self):
        """
        打开登录页面，并最大化窗口。
        注意：此处未添加显式等待，后续输入操作会等待元素出现。
        """
        self.driver.get(self.URL)
        self.driver.maximize_window()

    def input_login_info(self, username: str, password: str):
        """
        在用户名和密码输入框中输入信息。

        :param username: 用户名
        :param password: 密码
        :raises ValueError: 当用户名或密码为空时抛出异常
        """
        if not username or not password:
            raise ValueError("账号/密码不能为空")
        self.input_xpath(self.INPUT_USERNAME, username)
        self.input_xpath(self.INPUT_PASSWORD, password)

    def click_submit(self):
        """点击登录按钮。"""
        self.click_xpath(self.BTN_SUBMIT)

    def handle_exception_restart_popup(self):
        """
        处理登录后可能出现的“异常重启机制”弹窗。
        若弹窗在 1 秒内出现，则点击确认按钮关闭。
        """
        try:
            # 等待弹窗出现，超时 1 秒
            WebDriverWait(self.driver, 1).until(
                EC.visibility_of_element_located((By.XPATH, self.POPUP_EXCEPTION_RESTART))
            )
            print("[WARN] 检测到异常重启弹窗，正在关闭")
            if self.click_xpath(self.BTN_POPUP_CONFIRM, wait_time=2):
                print("[OK] 异常重启弹窗已关闭")
            else:
                print("[WARN] 弹窗按钮点击失败，已跳过")
        except TimeoutException:
            print("[OK] 无异常重启弹窗")
        except Exception as e:
            print(f"[WARN] 处理弹窗失败: {e}")

    def login(self, username: str = "superadmin", password: str = "Super678@!~"):
        """
        执行完整登录流程，包含页面打开、信息输入、点击登录、弹窗处理及成功验证。

        :param username: 用户名，默认为 superadmin
        :param password: 密码，默认为 Super678@!~
        :return: 登录成功返回 True
        """
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
        print("[OK] 登录成功")
        return True