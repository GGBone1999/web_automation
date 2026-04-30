# -*- coding: utf-8 -*-
"""
任务管理页面对象模块

封装任务管理页面的元素定位和操作：新建任务、编辑任务、删除任务、获取任务数量等。
所有定位统一使用 XPath/CSS，并基于 BasePage 提供的基础方法。
"""

import time
from utils.time_tools import dt_strftime
from base.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TaskPage(BasePage):
    """任务管理页面对象，继承自 BasePage，提供任务相关操作。"""

    # ===================== 左侧菜单定位 =====================
    BTN_TASK_ENTRY = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]'           # 任务父级菜单入口
    BTN_TASK_MENU = '/html/body/div[1]/div/div[2]/div/div[1]/ul/li/ul/li[7]'    # 任务管理子菜单

    # ===================== 任务列表操作 =====================
    BTN_NEW_TASK = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/button'  # 新建任务按钮
    LIST_TASKS = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li'            # 任务列表项
    BTN_EDIT = "(//span[text()='编辑'])[1]"                                                # 编辑按钮（第一个）
    BTN_DELETE = "(//button[contains(@class,'ivu-btn-error') and span[text()='删除']])[1]"  # 删除按钮（第一个）

    # ===================== 新增任务弹窗 =====================
    INPUT_TASK_NAME = "//div[contains(@class,'ivu-modal') and contains(.,'新增任务')]//div[contains(@class,'ivu-input-wrapper')]//input"  # 任务名称输入框
    BTN_ADD_CONFIRM = "//div[contains(@class,'ivu-modal') and contains(.,'新增任务')]//button[contains(.,'确定')]"                     # 新增弹窗“确定”按钮

    # ===================== 编辑任务弹窗 =====================
    BTN_EDIT_CONFIRM = "//div[contains(@class,'ivu-modal') and contains(.,'编辑任务')]//button[contains(.,'确定')]"                   # 编辑弹窗“确定”按钮

    # ===================== 删除确认弹窗 =====================
    BTN_DELETE_CONFIRM = "//div[contains(@class,'ivu-modal') and contains(.,'删除')]//button[contains(.,'确定')]"                     # 删除确认按钮

    # ===================== 添加路径图标 =====================
    ADD_PATH_ICON = "//div[contains(@class,'ivu-modal') and contains(.,'新增任务')]//div[contains(@class,'task-list')]//ul/li[2]//span[contains(@class,'bgBlue')]"  # 新增任务时添加路径的加号
    # 编辑任务时添加第二条路径（已修复定位）
    ADD_PATH_EDIT = "(//span[contains(@class,'bgBlue')])[2]"

    # ===================== 清洁模式选择 =====================
    CLEAN_MODE_SELECT = "//div[contains(@class,'ivu-modal') and contains(.,'编辑任务')]//div[contains(text(),'清洁模式')]/following::div[contains(@class,'ivu-select-selection') and .//span[text()='普通']][1]"  # 清洁模式下拉框
    CLEAN_MODE_DEEP = "//div[contains(@class,'ivu-modal') and contains(.,'编辑任务')]//li[contains(text(),'深度')]"                                      # 深度清洁模式选项

    def __init__(self, driver):
        """构造函数，调用父类初始化。"""
        super().__init__(driver)

    # ===================== 获取任务数量 =====================
    def get_task_count(self, retry=3):
        """
        获取任务列表中的任务数量，支持重试。
        :param retry: 最大重试次数
        :return: 任务数量（整数）
        """
        for i in range(retry):
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, self.LIST_TASKS))
                )
                return len(self.driver.find_elements(By.XPATH, self.LIST_TASKS))
            except:
                time.sleep(1)
        return 0

    # ===================== 辅助方法 =====================
    def click_clickable(self, xpath, timeout=10):
        """
        封装点击操作，调用 BasePage 的 click_xpath。
        :param xpath: 元素的 XPath 表达式
        :param timeout: 等待元素可点击的超时秒数
        """
        self.click_xpath(xpath, wait_time=timeout)

    # ===================== 进入任务页面 =====================
    def enter_task_page(self):
        """通过左侧菜单进入任务管理页面。"""
        self.click_xpath(self.BTN_TASK_ENTRY)
        time.sleep(2)
        self.clear_highlight()
        self.click_xpath(self.BTN_TASK_MENU)
        time.sleep(3)

    # ===================== 新建任务 =====================
    def create_new_task(self):
        """
        创建新任务，流程：
          1. 点击新建任务按钮
          2. 输入自动生成的任务名称（时间戳）
          3. 点击加号添加路径
          4. 点击确定保存任务
        """
        print('[INFO] 新增任务')
        # 注意：原代码为 self.get_task_count 缺少括号，此处保持原样（不执行）
        self.get_task_count
        time.sleep(1)
        self.click_xpath(self.BTN_NEW_TASK)
        time.sleep(3)

        self.wait_xpath(self.INPUT_TASK_NAME)
        task_name = dt_strftime("%Y%m%d%H%M%S")
        self.driver.find_element(By.XPATH, self.INPUT_TASK_NAME).send_keys(task_name)
        time.sleep(2)

        print("[ACTION] 点击加号添加路径")
        self.click_clickable(self.ADD_PATH_ICON)
        time.sleep(0.5)

        print("[ACTION] 新增弹窗 点击确定保存任务")
        self.click_clickable(self.BTN_ADD_CONFIRM)
        time.sleep(3)

    # ===================== 编辑任务 =====================
    def edit_task(self):
        """
        编辑第一个任务，流程：
          1. 点击编辑按钮
          2. 将清洁模式改为“深度”
          3. 添加第二条路径
          4. 点击确定保存
        """
        time.sleep(2)

        self.click_xpath(self.BTN_EDIT)
        time.sleep(3)

        # 选择清洁模式
        self.click_clickable(self.CLEAN_MODE_SELECT)
        time.sleep(1)
        self.click_clickable(self.CLEAN_MODE_DEEP)
        time.sleep(1)

        # 添加第二条路径
        print("[ACTION] 编辑时添加第二条路径")
        self.click_clickable(self.ADD_PATH_EDIT)
        time.sleep(1)

        # 编辑弹窗 点击确定保存
        print("[ACTION] 编辑弹窗 点击确定保存")
        self.click_clickable(self.BTN_EDIT_CONFIRM)
        time.sleep(2)

    # ===================== 删除任务 =====================
    def delete_task(self):
        """
        删除第一个任务，流程：
          1. 点击删除按钮
          2. 在确认弹窗中点击确定
        """
        time.sleep(1)
        self.click_clickable(self.BTN_DELETE)
        time.sleep(1)

        print("[ACTION] 确认删除")
        self.click_clickable(self.BTN_DELETE_CONFIRM)
        time.sleep(3)