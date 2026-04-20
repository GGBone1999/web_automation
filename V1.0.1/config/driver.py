from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from config.settings import BROWSER, URL, TIMEOUT

class Driver:
    def __init__(self):
        self.driver = self._init_driver()
        self.driver.maximize_window()
        self.driver.get(URL)
        self.wait = WebDriverWait(self.driver, TIMEOUT)

    def _init_driver(self):
        if BROWSER == "chrome":
            return webdriver.Chrome()
        elif BROWSER == "firefox":
            return webdriver.Firefox()

    def quit(self):
        self.driver.quit()