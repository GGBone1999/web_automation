from selenium.webdriver.common.by import By
from base.base_page import BasePage
from config.settings import USERNAME, PASSWORD

class MainPage(BasePage):
    # === 元素定位 ===
    username_input = (By.XPATH, "//input[@placeholder='账号']")
    password_input = (By.XPATH, "//input[@placeholder='密码']")
    login_btn = (By.XPATH, "//span[text()='登录']")

    # === 页面操作 ===
    def login(self):
        self.input(self.username_input, USERNAME)
        self.input(self.password_input, PASSWORD)
        self.click(self.login_btn)

    # 你原来test_clean.py里的所有点击/输入/操作
    # 全部按这个格式搬到这里
    def click_menu(self):
        self.click((By.XPATH, "//*[text()='你菜单的文字']"))

    def search_data(self):
        self.click((By.XPATH, "//*[text()='查询']"))