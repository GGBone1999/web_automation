import time
import pyautogui
from utils.time_tools import dt_strftime
from base.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RoutePage(BasePage):
    """
    路线管理页面
    功能：示教路径创建（3个确定按钮）、普通路线创建、编辑、删除等完整操作
    第一个确定按钮使用XPath定位，第二、三个确定按钮使用屏幕坐标点击
    """

    # ===================== 左侧菜单元素 =====================
    BTN_PARENT_MENU = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div'
    BTN_ROUTE_ENTRY = '/html/body/div[1]/div/div[2]/div/div[1]/ul/li/ul/li[6]'

    # ===================== 示教路径相关元素 =====================
    BTN_NEW_TEACH_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[1]/button'
    INPUT_TEACH_NAME = '.directPathName > div:nth-child(1) > input:nth-child(2)'
    
    # ✅ 你要的精准稳定定位（已替换）
    BTN_CONFIRM_1 = "//div[contains(@class,'ivu-modal') and .//div[contains(@class,'ivu-modal-header') and contains(.,'示教清洁路线名称')]]//button[contains(@class,'ivu-btn-primary') and normalize-space()='确定']"

    # ===================== 普通路线相关元素 =====================
    BTN_NEW_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/button[1]'
    INPUT_ROUTE_NAME = '.routeModal > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > input:nth-child(2)'
    BTN_ROUTE_TYPE = '.routeModal > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > button:nth-child(2)'
    BTN_DRAW_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/button[1]'
    BTN_FILL_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/button[2]'
    BTN_SAVE_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/button[4]'
    BTN_SAVE_CONFIRM = '/html/body/div[16]/div[2]/div/div/div[3]/div/button[2]'

    # ===================== 路线编辑/删除相关元素 =====================
    LIST_ROUTES = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li'
    BTN_CONFIRM_DELETE = '.ivu-modal-confirm-footer > button:nth-child(2)'
    BTN_EDIT_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li[1]/div[2]/button[1]'

    def __init__(self, driver):
        super().__init__(driver)
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3

    # ===================== 进入页面 =====================
    def enter_route_page(self):
        time.sleep(1)
        self.click_xpath(self.BTN_PARENT_MENU)
        time.sleep(3)
        self.clear_highlight()
        self.click_xpath(self.BTN_ROUTE_ENTRY)
        time.sleep(3)

    # ===================== 新建示教路径 =====================
    def create_teach_route(self):
        self.get_route_count
        time.sleep(3)
        self.click_xpath(self.BTN_NEW_TEACH_ROUTE)

        name = dt_strftime("%Y%m%d%H%M%S")
        self.input_css(self.INPUT_TEACH_NAME, name)
        time.sleep(2)

        print("[表情] 点击第1个确定（xpath）")
        self.wait_xpath(self.BTN_CONFIRM_1)
        self.click_xpath(self.BTN_CONFIRM_1)
        time.sleep(3)

        print("[表情] 点击第2个确定（坐标）")
        pyautogui.click(x=1845, y=283)
        time.sleep(3)

        print("[表情] 点击第3个确定（坐标）")
        pyautogui.click(x=1864, y=991)
        time.sleep(4)

    # ===================== 创建手绘路线 =====================
    def create_normal_route(self):
        self.click_xpath(self.BTN_NEW_ROUTE)
        time.sleep(2)
        name = dt_strftime("%Y%m%d%H%M%S")
        self.input_css(self.INPUT_ROUTE_NAME, name)
        self.click_css(self.BTN_ROUTE_TYPE)
        time.sleep(2)

        self.click_xpath(self.BTN_DRAW_ROUTE)
        pyautogui.mouseDown(x=938, y=739)
        pyautogui.moveTo(x=985, y=465, duration=1)
        pyautogui.mouseUp()
        time.sleep(2)

        self.click_xpath(self.BTN_SAVE_ROUTE)
        time.sleep(1)
        
        # ✅ 已替换为坐标点击
        pyautogui.click(x=1864, y=991)
        time.sleep(3)
        
        self.wait_xpath("//div[@class='ivu-message-notice-content']")
        time.sleep(2)
        pyautogui.click(x=50, y=50)
        time.sleep(3)

    # ===================== 创建填充路线 =====================
    def create_fillin_route(self):
        self.click_xpath(self.BTN_NEW_ROUTE)
        time.sleep(1)
        name = dt_strftime("%Y%m%d%H%M%S")
        self.input_css(self.INPUT_ROUTE_NAME, name)
        self.click_css(self.BTN_ROUTE_TYPE)
        time.sleep(1)

        self.click_xpath(self.BTN_FILL_ROUTE)
        pyautogui.click(x=1116, y=859)
        pyautogui.click(x=733, y=848)
        pyautogui.click(x=1122, y=358)
        pyautogui.click(x=743, y=357)
        time.sleep(2)

        self.click_xpath(self.BTN_SAVE_ROUTE)
        time.sleep(1)
        
        # ✅ 已替换为坐标点击
        pyautogui.click(x=1864, y=991)
        time.sleep(4)
        self.wait_xpath("//div[@class='ivu-message-notice-content']")
        time.sleep(2)

    # ===================== 编辑路线 =====================
    def edit_route(self):
        time.sleep(2)
        self.click_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/button[3]')
        time.sleep(1)
        pyautogui.click(x=1114, y=859)
        time.sleep(0.5)
        pyautogui.mouseDown(x=1114, y=859)
        pyautogui.moveTo(x=1111, y=698, duration=1)
        pyautogui.mouseUp()
        time.sleep(2)
        self.click_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/button[4]')
        time.sleep(2)

    # ===================== 删除路线 =====================
    def get_route_count(self, retry=3):
        for i in range(retry):
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, self.LIST_ROUTES))
                )
                return len(self.driver.find_elements(By.XPATH, self.LIST_ROUTES))
            except:
                time.sleep(2)
        return 0

    def delete_route(self, route_count=None):
        """删除最后3条路线"""
        time.sleep(2)
        for _ in range(3):
            del_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li[last()]/div[2]/button[2]"
            self.click_xpath(del_xpath)
            time.sleep(2)
            self.click_css(self.BTN_CONFIRM_DELETE)
            time.sleep(2)