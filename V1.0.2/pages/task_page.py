import time
from utils.time_tools import dt_strftime
from base.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TaskPage(BasePage):
    """任务页面（所有定位统一管理）"""

    # ===================== 左侧菜单 =====================
    BTN_TASK_ENTRY = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]'
    BTN_TASK_MENU = '/html/body/div[1]/div/div[2]/div/div[1]/ul/li/ul/li[7]'

    # ===================== 任务列表 =====================
    BTN_NEW_TASK = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/button'
    LIST_TASKS = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[2]/ul/li'
    BTN_EDIT = "(//span[text()='编辑'])[1]"
    BTN_DELETE = "(//button[contains(@class,'ivu-btn-error') and span[text()='删除']])[1]"

    # ===================== 【新增任务】弹窗 =====================
    INPUT_TASK_NAME = "//div[contains(@class,'ivu-modal') and contains(.,'新增任务')]//div[contains(@class,'ivu-input-wrapper')]//input"
    BTN_ADD_CONFIRM = "//div[contains(@class,'ivu-modal') and contains(.,'新增任务')]//button[contains(.,'确定')]"

    # ===================== 【编辑任务】弹窗 =====================
    BTN_EDIT_CONFIRM = "//div[contains(@class,'ivu-modal') and contains(.,'编辑任务')]//button[contains(.,'确定')]"

    # ===================== 【删除】确认弹窗 =====================
    BTN_DELETE_CONFIRM = "//div[contains(@class,'ivu-modal') and contains(.,'删除')]//button[contains(.,'确定')]"

    # ===================== 添加路径 =====================
    ADD_PATH_ICON = "//div[contains(@class,'ivu-modal') and contains(.,'新增任务')]//div[contains(@class,'task-list')]//ul/li[2]//span[contains(@class,'bgBlue')]"
    # ✅ 已修复：编辑任务添加第二条路径
    ADD_PATH_EDIT = "(//span[contains(@class,'bgBlue')])[2]"

    # ===================== 清洁模式 =====================
    CLEAN_MODE_SELECT = "//div[contains(@class,'ivu-modal') and contains(.,'编辑任务')]//div[contains(text(),'清洁模式')]/following::div[contains(@class,'ivu-select-selection') and .//span[text()='普通']][1]"
    CLEAN_MODE_DEEP = "//div[contains(@class,'ivu-modal') and contains(.,'编辑任务')]//li[contains(text(),'深度')]"

    def __init__(self, driver):
        super().__init__(driver)

    # ===================== 新增：获取任务数量 =====================
    def get_task_count(self, retry=3):
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
        self.click_xpath(xpath, wait_time=timeout)

    # ===================== 进入页面 =====================
    def enter_task_page(self):
        self.click_xpath(self.BTN_TASK_ENTRY)
        time.sleep(2)
        self.clear_highlight()
        self.click_xpath(self.BTN_TASK_MENU)
        time.sleep(3)

    # ===================== 新建任务 =====================
    def create_new_task(self):
        print('新增任务')
        self.get_task_count
        time.sleep(1)
        self.click_xpath(self.BTN_NEW_TASK)
        time.sleep(3)

        self.wait_xpath(self.INPUT_TASK_NAME)
        task_name = dt_strftime("%Y%m%d%H%M%S")
        self.driver.find_element(By.XPATH, self.INPUT_TASK_NAME).send_keys(task_name)
        time.sleep(2)

        print("👉 点击加号添加路径")
        self.click_clickable(self.ADD_PATH_ICON)
        time.sleep(0.5)

        print("👉 【新增弹窗】点击确定保存任务")
        self.click_clickable(self.BTN_ADD_CONFIRM)
        time.sleep(3)

    # ===================== 编辑任务 =====================
    def edit_task(self):
        time.sleep(2)

        self.click_xpath(self.BTN_EDIT)
        time.sleep(3)

        # 选择清洁模式
        self.click_clickable(self.CLEAN_MODE_SELECT)
        time.sleep(1)
        self.click_clickable(self.CLEAN_MODE_DEEP)
        time.sleep(1)

        # 添加第二条路径
        print("👉 编辑时添加第二条路径")
        self.click_clickable(self.ADD_PATH_EDIT)
        time.sleep(1)

        # 【编辑弹窗】点击确定保存
        print("👉 【编辑弹窗】点击确定保存")
        self.click_clickable(self.BTN_EDIT_CONFIRM)
        time.sleep(2)

    # ===================== 删除任务 =====================
    def delete_task(self):
        time.sleep(1)
        self.click_clickable((By.XPATH, self.BTN_DELETE))
        time.sleep(1)

        print("👉 确认删除")
        self.click_clickable(self.BTN_DELETE_CONFIRM)
        time.sleep(3)