import time
from utils.time_tools import dt_strftime
import pyautogui
from base.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TaskPage(BasePage):
    """任务页面"""
    
    # 定位
    BTN_TASK_ENTRY = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]'
    BTN_TASK_MENU = '/html/body/div[1]/div/div[2]/div/div[1]/ul/li/ul/li[7]'
    BTN_NEW_TASK = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/button'
    INPUT_TASK_NAME = 'div.ivu-input-wrapper:nth-child(2) > div:nth-child(1) > input:nth-child(2)'
    LIST_TASKS = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li'

    def __init__(self, driver):
        super().__init__(driver)

    def enter_task_page(self):
        """进入任务页面"""
        self.click_xpath(self.BTN_TASK_ENTRY)
        time.sleep(5)
        self.click_xpath(self.BTN_TASK_MENU)
        time.sleep(3)

    def wait_for_preActived_element(self, timeout=10):
        """等待 .preActived 元素出现"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.preActived'))
            )
            return element
        except:
            fallback_selectors = [
                '.preActive',
                '[class*="preAct"]',
                '.active',
                '[class*="act"]',
            ]
            
            for selector in fallback_selectors:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    return element
                except:
                    continue
            
            raise Exception("无法找到预激活元素")

    def create_new_task(self):
        """新增任务"""
        print('新增任务')
        self.enter_task_page()
    
        self.click_xpath(self.BTN_NEW_TASK)
        time.sleep(2)
    
        self.wait_css(self.INPUT_TASK_NAME)
        task_name = dt_strftime("%Y%m%d%H%M%S")
        self.driver.find_element(By.CSS_SELECTOR, self.INPUT_TASK_NAME).send_keys(task_name)
        time.sleep(1)

        # 点击界面显示红色高亮
        self.click_xpath("/html/body/div[13]/div[2]/div/div/div[2]/div/div[1]/div[9]/ul[2]/li[2]/span[2]")
        time.sleep(0.5)

        pyautogui.click(x=1861, y=998)
        time.sleep(3)

    def edit_task(self):
        """编辑任务"""
        time.sleep(2)

        edit_btn_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li/div[2]/button[1]"
        self.click_xpath(edit_btn_xpath)
        time.sleep(2)

        # 点击清洁模式显示红色高亮
        clean_mode_xpath = "/html/body/div[13]/div[2]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/span"
        self.click_xpath(clean_mode_xpath)
        time.sleep(0.5)

        deep_mode_xpath = "/html/body/div[13]/div[2]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/ul[2]/li[4]"
        self.click_xpath(deep_mode_xpath)
        time.sleep(0.5)

        # 点击添加路径显示红色高亮
        add_second_path_xpath = "/html/body/div[13]/div[2]/div/div/div[2]/div/div[1]/div[9]/ul[2]/li[3]/span[2]"
        self.click_xpath(add_second_path_xpath)
        time.sleep(0.5)

        pyautogui.click(x=1861, y=998)
        time.sleep(2)


    def delete_task(self):
        """删除任务"""
        time.sleep(1)

        delete_btn_xpath = '//button[contains(@class,"ivu-btn-error") and span[text()="删除"]]'
        self.click_xpath(delete_btn_xpath)
        time.sleep(1)

        print("👉 坐标点击确认删除")
        pyautogui.click(x=1166, y=422)
        time.sleep(2)