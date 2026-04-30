# -*- coding: utf-8 -*-
"""
路线管理页面对象模块

封装路线管理页面（示教路线、普通路线、填充路线）的创建、编辑、删除等操作。
使用 XPath 和屏幕坐标混合定位。
"""

import time
import pyautogui
from utils.time_tools import dt_strftime
from base.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RoutePage(BasePage):
    """
    路线管理页面对象，继承自 BasePage。
    提供示教路径创建（3个确定按钮）、普通路线创建、手动绘制、填充路线、编辑、删除等功能。
    """

    # ===================== 左侧菜单元素 =====================
    BTN_PARENT_MENU = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div'   # 父级菜单（可能是“更多”或“工具”）
    BTN_ROUTE_ENTRY = '/html/body/div[1]/div/div[2]/div/div[1]/ul/li/ul/li[6]'  # 路线管理入口

    # ===================== 示教路径相关元素 =====================
    BTN_NEW_TEACH_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[1]/button'  # “新建示教路线”按钮
    INPUT_TEACH_NAME = '.directPathName > div:nth-child(1) > input:nth-child(2)'  # 示教路线名称输入框（CSS）

    # 示教路线第一个确定按钮（精准定位弹窗中的确认按钮）
    BTN_CONFIRM_1 = "//div[contains(@class,'ivu-modal') and .//div[contains(@class,'ivu-modal-header') and contains(.,'示教清洁路线名称')]]//button[contains(@class,'ivu-btn-primary') and normalize-space()='确定']"

    # ===================== 普通路线相关元素 =====================
    BTN_NEW_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/button[1]'  # 新建普通路线按钮
    INPUT_ROUTE_NAME = '.routeModal > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > input:nth-child(2)'  # 路线名称输入框
    BTN_ROUTE_TYPE = '.routeModal > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > button:nth-child(2)'  # 路线类型选择按钮
    BTN_DRAW_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/button[1]'  # 手绘路线按钮
    BTN_FILL_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/button[2]'  # 填充路线按钮
    BTN_SAVE_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/button[4]'  # 保存路线按钮
    BTN_SAVE_CONFIRM = '/html/body/div[16]/div[2]/div/div/div[3]/div/button[2]'  # 保存确认按钮

    # ===================== 路线编辑/删除相关元素 =====================
    LIST_ROUTES = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li'  # 路线列表项
    BTN_CONFIRM_DELETE = '.ivu-modal-confirm-footer > button:nth-child(2)'         # 删除确认按钮
    BTN_EDIT_ROUTE = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li[1]/div[2]/button[1]'  # 编辑第一条路线按钮

    def __init__(self, driver):
        """
        构造函数，调用父类初始化，并配置 pyautogui 参数。
        :param driver: WebDriver 实例
        """
        super().__init__(driver)
        pyautogui.FAILSAFE = True   # 启用安全模式（鼠标移到角落可中断）
        pyautogui.PAUSE = 0.3       # 每次 pyautogui 操作后暂停 0.3 秒

    # ===================== 进入页面 =====================
    def enter_route_page(self):
        """通过左侧菜单进入路线管理页面。"""
        time.sleep(1)
        self.click_xpath(self.BTN_PARENT_MENU)
        time.sleep(3)
        self.clear_highlight()
        self.click_xpath(self.BTN_ROUTE_ENTRY)
        time.sleep(3)

    # ===================== 新建示教路径 =====================
    def create_teach_route(self):
        """
        创建示教清洁路线。
        流程：点击新建 -> 输入名称 -> 点击第一个确定（XPath）-> 点击第二、三个确定（屏幕坐标）。
        """
        # 注意：原代码中 self.get_route_count 缺少括号，但保持原始写法不加修改
        self.get_route_count
        time.sleep(5)
        self.click_xpath(self.BTN_NEW_TEACH_ROUTE)

        name = dt_strftime("%Y%m%d%H%M%S")
        self.input_css(self.INPUT_TEACH_NAME, name)
        time.sleep(2)

        print("[INFO] 点击第1个确定（xpath）")
        self.wait_xpath(self.BTN_CONFIRM_1)
        self.click_xpath(self.BTN_CONFIRM_1)
        time.sleep(3)

        print("[INFO] 点击第2个确定（坐标）")
        pyautogui.click(x=1845, y=283)
        time.sleep(3)

        print("[INFO] 点击第3个确定（坐标）")
        pyautogui.click(x=1864, y=991)
        time.sleep(4)

    # ===================== 创建手绘路线 =====================
    def create_normal_route(self):
        """
        创建普通路线（手绘模式）。
        流程：新建路线 -> 输入名称 -> 选择类型 -> 点击手绘按钮 -> 在画布上拖拽绘制 -> 保存 -> 确认。
        """
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

        # 使用屏幕坐标点击保存确认按钮
        pyautogui.click(x=1864, y=991)
        time.sleep(3)

        self.wait_xpath("//div[@class='ivu-message-notice-content']")
        time.sleep(2)
        pyautogui.click(x=50, y=50)
        time.sleep(3)

    # ===================== 创建填充路线 =====================
    def create_fillin_route(self):
        """
        创建填充路线（通过点击多个点生成闭合区域）。
        流程：新建路线 -> 输入名称 -> 选择类型 -> 点击填充路线按钮 -> 点击多个坐标点 -> 保存 -> 确认。
        """
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

        # 使用屏幕坐标点击保存确认按钮
        pyautogui.click(x=1864, y=991)
        time.sleep(4)
        self.wait_xpath("//div[@class='ivu-message-notice-content']")
        time.sleep(2)

    # ===================== 编辑路线 =====================
    def edit_route(self):
        """
        编辑第一条路线（通过点击编辑按钮，用 pyautogui 拖拽调整路线形状）。
        """
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

    # ===================== 获取路线数量 =====================
    def get_route_count(self, retry=3):
        """
        获取路线列表中的路线数量，支持重试。
        :param retry: 最大重试次数
        :return: 路线数量（整数）
        """
        for i in range(retry):
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, self.LIST_ROUTES))
                )
                return len(self.driver.find_elements(By.XPATH, self.LIST_ROUTES))
            except:
                time.sleep(2)
        return 0

    # ===================== 删除路线 =====================
    def delete_route(self, route_count=None):
        """
        删除最后 3 条路线（循环删除列表末尾的路线）。
        :param route_count: 本参数未被使用，保持原始方法签名
        """
        time.sleep(2)
        for _ in range(3):
            del_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li[last()]/div[2]/button[2]"
            self.click_xpath(del_xpath)
            time.sleep(2)
            self.click_css(self.BTN_CONFIRM_DELETE)
            time.sleep(2)