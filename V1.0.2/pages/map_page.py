import time
import os
from utils.time_tools import dt_strftime
from base.base_page import BasePage
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# 新增：导入环境配置
from config.env_config import ENV_2D, ENV_3D


class MapPage(BasePage):

    # ===================== 基础页面元素定位 =====================
    # 菜单入口
    TASK_SETTING = "//*[contains(text(),'任务设置')]"
    BTN_MAP_ENTRY = "//*[contains(text(),'地图管理')]"

    # 地图列表
    LIST_MAPS = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div'
    BTN_NEW_MAP = "/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[1]/button"

    # 新建地图弹窗
    INPUT_MAP_NAME = "//input[@placeholder='输入地图名称']"
    BTN_MAP_CONFIRM = "//input[@placeholder='输入地图名称']/ancestor::div[contains(@class, 'ivu-modal')]//button[span[text()='确定']]"

    # 地图操作按钮
    BTN_CANCEL_MAP = 'button.mapButton:nth-child(2)'
    BTN_CONFIRM_MAP = 'button.mapButton:nth-child(3)'
    BTN_SAVE_MAP = '.ivu-modal-confirm-footer > button:nth-child(1)'

    # ===================== 指定4个按钮（地图下按钮无文字） =====================
    # 设置默认地图
    BTN_SET_DEFAULT = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[1]/div[1]'
    # 编辑地图
    BTN_EDIT_MAP = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[4]/div[1]'
    # 删除地图
    BTN_DELETE_MAP = lambda self, index: f"(//i[contains(@class,'ico-15')])[{index}]"
    # 扩展地图（默认3D，初始化时覆盖）
    BTN_EXPAND_MAP = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[7]/div[1]'

    # ===================== 编辑/拓展相关元素定位（文本嵌套） =====================
    # 清除噪点
    BTN_EDIT_ENTRY = "//*[text()='清除噪点']/ancestor::button[1]"
    # 保存噪点框
    BTN_SAVE_NOISE = "//*[text()='保存噪点框']/ancestor::button[1]"
    # 退出编辑
    BTN_EXIT_EDIT = "//*[text()='退出']/ancestor::button[1]"

    # 扩展确认
    BTN_EXPAND_CONFIRM = "//div[contains(@class,'ivu-modal') and .//div[contains(@class,'ivu-modal-header') and contains(.,'注意')]]//button[contains(@class,'ivu-btn-primary') and normalize-space()='确定']"
    BTN_NAVIGATE_ITEM = '.navigate-item'
    BTN_SURE = '.sure'
    BTN_EXPAND_CANCEL = 'button.mapButton:nth-child(2)'
    BTN_MODAL_FIRST = '.ivu-modal-confirm-footer > button:nth-child(1)'

    # 通用弹窗
    BTN_CONFIRM_DELETE = "//div[contains(@class,'ivu-modal') and contains(.,'确定删除地图')]//button[contains(@class,'ivu-btn-primary') and normalize-space()='确定']"
    INPUT_UPLOAD_FILE = "//input[@type='file']"  # 这是 XPath

    # ===================== 重定位功能元素 =====================
    BTN_RELOCATE_ENTRY = "//*[contains(text(),'运动控制')]"
    BTN_RELOCATE_START = "//*[contains(text(),'导航模式')]"
    BTN_RELOCATE_CONFIRM = "(//*[contains(text(),'矫正定位')])[1]"
    BTN_RELOCATE_SUBMIT = '.ivu-modal-confirm-footer > button:nth-child(2)'
    BTN_RELOCATE_SAVE = '.ivu-modal-confirm-footer > button:nth-child(1)'

    # ===================== 遥控模式入口 =====================
    BTN_REMOTE_MODE = "//*[contains(text(),'遥控模式')]"

    # ===================== 初始化 =====================
    def __init__(self, driver, env="2d"):
        super().__init__(driver)
        # 新增：根据环境加载差异化配置
        self.env = env.lower()
        self.env_config = ENV_2D if self.env == "2d" else ENV_3D
        # 覆盖扩展地图按钮定位
        self.BTN_EXPAND_MAP = self.env_config["MAP_PAGE"]["BTN_EXPAND_MAP"]
        # 保存重定位坐标
        self.relocate_coord = self.env_config["MAP_PAGE"]["RELOCATE_COORD"]
        # 保存上传文件列表
        self.upload_files = self.env_config["MAP_PAGE"]["UPLOAD_FILES"]

    # ===================== 公共方法 =====================
    def enter_remote_mode(self):
        self.close_all_modal()
        time.sleep(1)
        """进入遥控模式"""
        print("👉 进入遥控模式")
        self.click_xpath(self.BTN_REMOTE_MODE)
        time.sleep(1)

    def enter_map_page(self):
        """进入地图管理页面"""
        self.click_xpath(self.TASK_SETTING)
        time.sleep(1)
        self.clear_highlight()
        self.click_xpath(self.BTN_MAP_ENTRY)
        time.sleep(2)

    # ===================== 修复：地图数量获取（去掉超时陷阱） =====================
    def get_map_count(self, retry=3):
        """获取地图数量，支持重试和显式等待"""
        for i in range(retry):
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, self.LIST_MAPS))
                )
                elements = self.driver.find_elements(By.XPATH, self.LIST_MAPS)
                count = len(elements)
                if count > 0 or i == retry-1:
                    return count
                time.sleep(1)
            except:
                time.sleep(1)
        return 0

    # ===================== 取消创建地图 =====================
    def cancel_create_map(self):
        count_before = self.get_map_count()
        print(f"取消建图前数量: {count_before}")
        time.sleep(1)
        self.click_xpath(self.BTN_NEW_MAP)
        time.sleep(2)
        self.input_xpath(self.INPUT_MAP_NAME, dt_strftime("%Y%m%d%H%M%S"))
        time.sleep(2)
        self.click_xpath(self.BTN_MAP_CONFIRM)
        time.sleep(5)

        self.wait_css(self.BTN_CANCEL_MAP)
        self.click_css(self.BTN_CANCEL_MAP)

        count_after = self.get_map_count()
        print(f"取消建图后数量: {count_after}")
        time.sleep(5)

    # ===================== 创建新地图 =====================
    def create_new_map(self, map_name: str = "自动化地图"):
        count_before = self.get_map_count()
        print(f"新建地图前数量: {count_before}")
        time.sleep(2)
        self.click_xpath(self.BTN_NEW_MAP)
        time.sleep(3)
        self.input_xpath(self.INPUT_MAP_NAME, dt_strftime("%Y%m%d%H%M%S"))
        self.click_xpath(self.BTN_MAP_CONFIRM)
        time.sleep(30)

        self.wait_css(self.BTN_CONFIRM_MAP)
        self.click_css(self.BTN_CONFIRM_MAP)
        print("点击确定建图")

        self.wait_css(self.BTN_SAVE_MAP)
        self.click_css(self.BTN_SAVE_MAP)
        time.sleep(5)

        count_after = self.get_map_count()
        print(f"新建地图后数量: {count_after}")
        time.sleep(7)

    # ===================== 编辑地图 =====================
    def edit_map(self, map_index: int):
        """
        编辑地图标准流程
        :param map_index: 地图索引（从1开始）
        """
        self.wait_xpath(self.BTN_EDIT_MAP(map_index))
        self.click_xpath(self.BTN_EDIT_MAP(map_index))
        time.sleep(3)

        self.wait_xpath(self.BTN_EDIT_ENTRY)
        self.click_xpath(self.BTN_EDIT_ENTRY)
        time.sleep(3)

        self.pyautogui_click(771, 505)
        time.sleep(1)
        self.pyautogui_click(838, 669)
        time.sleep(1)
        self.pyautogui_click(993, 506)
        time.sleep(2)

        try:
            self.wait_xpath(self.BTN_SAVE_NOISE)
            self.click_xpath(self.BTN_SAVE_NOISE)
        except:
            self.click_css("div[class*='btn']:last-child")
        time.sleep(3)

        try:
            self.wait_xpath(self.BTN_EXIT_EDIT)
            self.click_xpath(self.BTN_EXIT_EDIT)
        except:
            pass
        time.sleep(3)

    # ===================== 扩展地图 =====================
    def expand_map(self, map_index: int):
        # 点击扩展按钮并确认（使用环境适配后的定位）
        time.sleep(1)
        self.click_xpath(self.BTN_EXPAND_MAP(map_index))
        time.sleep(5)
        self.click_xpath(self.BTN_EXPAND_CONFIRM)
        time.sleep(5)

        # 点击导航项并在画布打点
        self.click_css(self.BTN_NAVIGATE_ITEM)
        self.pyautogui_click(771, 505)
        time.sleep(5)

        # 点击取消按钮 → 确认保存
        self.click_css(self.BTN_EXPAND_CANCEL)
        self.wait_css(self.BTN_MODAL_FIRST)
        self.click_css(self.BTN_MODAL_FIRST)
        time.sleep(5)

        # 点击提示确定 → 返回地图页 → 最终确认
        self.click_css(self.BTN_SURE)
        time.sleep(10)
        self.wait_xpath(self.BTN_MAP_ENTRY)
        self.wait_css(self.BTN_MODAL_FIRST)
        self.click_css(self.BTN_MODAL_FIRST)

    # ===================== 删除地图 =====================
    def delete_map(self, map_index: int):
        count_before = self.get_map_count()
        print(f"删除地图前数量: {count_before}")

        self.click_xpath(self.BTN_DELETE_MAP(map_index))
        time.sleep(2)  # 修复：等待弹窗出现
        
        self.wait_xpath(self.BTN_CONFIRM_DELETE)  # 修复：等待元素出现
        self.click_xpath(self.BTN_CONFIRM_DELETE)

        time.sleep(3)
        count_after = self.get_map_count()
        print(f"删除地图后数量: {count_after}")

    # ===================== 上传地图（适配环境差异化文件顺序） =====================
    def upload_map(self):
        self.close_all_modal()
        count_before = self.get_map_count()
        print(f"上传地图前数量: {count_before}")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

        # 适配环境差异化的文件上传顺序
        for file_name in self.upload_files:
            file_path = os.path.join(data_dir, file_name)
            upload_input = self.find_xpath(self.INPUT_UPLOAD_FILE)
            upload_input.send_keys(file_path)
            time.sleep(3)
            print(f"✅ {file_name} 上传成功")
            time.sleep(1)

        count_after = self.get_map_count()
        assert count_after == count_before + 2, f"上传后地图数量异常"
        print("✅ 地图上传验证通过")
        time.sleep(5)

    # ===================== 设置第一张为默认地图 =====================
    def set_first_map_default(self):
        print("✅ 正在设置【第一张】地图为默认...")
        self.click_xpath(self.BTN_SET_DEFAULT(1))
        time.sleep(3)
        print("✅ 第一张地图已设置为默认")

    # ===================== 设置最后一张为默认地图 =====================
    def set_last_map_default(self):
        total = self.get_map_count()
        print(f"当前地图总数：{total}，正在设置最后一张为默认...")
        self.click_xpath(self.BTN_SET_DEFAULT(total))
        time.sleep(3)
        print(f"✅ 第 {total} 张地图已设置为默认")

    # ===================== 地图重定位（适配环境差异化坐标） =====================
    def relocate(self):
        print(f"开始矫正定位（{self.env.upper()}环境）")
        self.click_xpath(self.BTN_RELOCATE_ENTRY)
        time.sleep(3)
        self.click_xpath(self.BTN_RELOCATE_START)
        time.sleep(3)
        self.click_xpath(self.BTN_RELOCATE_CONFIRM)
        time.sleep(3)

        # 使用环境适配后的重定位坐标
        x1, y1, x2, y2 = self.relocate_coord
        self.pyautogui_drag(x1, y1, x2, y2)
        time.sleep(15)

        # 修复：CSS 必须用 click_css
        self.click_css(self.BTN_RELOCATE_SUBMIT)
        time.sleep(20)
        self.click_css(self.BTN_RELOCATE_SAVE)
        time.sleep(5)
        self.click_xpath(self.BTN_REMOTE_MODE)

    # ===================== 删除最后一张地图 =====================
    def delete_last_map(self):
        total = self.get_map_count()
        if total < 1:
            print("ℹ️ 没有地图可删除")
            return
        print(f"当前共 {total} 张地图 → 即将删除最后一张")
        self.delete_map(total)