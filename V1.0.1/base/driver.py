from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config.settings import BROWSER, URL, TIMEOUT

class Driver:
    def __init__(self):
        self.driver = self._init_driver()
        self.driver.maximize_window()
        # 设置页面缩放为90%
        self.set_zoom(0.9)
        self.driver.get(URL)
        self.driver.implicitly_wait(5)

    def _init_driver(self):
        if BROWSER == "chrome":
            chrome_options = Options()
            # 通过Chrome参数设置缩放
            chrome_options.add_argument("--force-device-scale-factor=0.9")
            chrome_options.add_argument("--zoom=90%")
            return webdriver.Chrome(options=chrome_options)
        elif BROWSER == "firefox":
            return webdriver.Firefox()
        else:
            # 默认使用Chrome
            chrome_options = Options()
            chrome_options.add_argument("--force-device-scale-factor=0.9")
            chrome_options.add_argument("--zoom=90%")
            return webdriver.Chrome(options=chrome_options)

    def set_zoom(self, zoom_level=0.9):
        """设置页面缩放"""
        self.driver.execute_script(f"document.body.style.zoom='{zoom_level}'")

    def quit(self):
        self.driver.quit()