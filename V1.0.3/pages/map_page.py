# -*- coding: utf-8 -*-
"""
地图管理页面对象模块

封装地图管理页面（包括地图列表、创建、编辑、删除、上传、重定位等）的所有操作。
支持 2D / 3D 环境差异化配置（通过 env_config 加载不同的坐标、文件顺序等）。
"""

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
# 导入环境配置（2D / 3D 差异化参数）
from config.env_config import ENV_2D, ENV_3D


class MapPage(BasePage):
    """
    地图页面对象，继承自 BasePage。
    提供地图的增、删、改、查、上传、扩展、重定位、设置默认等业务方法。
    """

    # ===================== 基础页面元素定位 =====================
    TASK_SETTING = "//*[contains(text(),'任务设置')]"                     # 左侧菜单“任务设置”
    BTN_MAP_ENTRY = "//*[contains(text(),'地图管理')]"                   # 子菜单“地图管理”入口

    LIST_MAPS = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div'   # 地图列表容器
    BTN_NEW_MAP = "/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[1]/button"  # “新建地图”按钮

    # 新建地图弹窗
    INPUT_MAP_NAME = "//input[@placeholder='输入地图名称']"                # 地图名称输入框
    BTN_MAP_CONFIRM = "//input[@placeholder='输入地图名称']/ancestor::div[contains(@class, 'ivu-modal')]//button[span[text()='确定']]"  # 弹窗“确定”按钮

    # 地图操作按钮（取消、确认、保存）
    BTN_CANCEL_MAP = 'button.mapButton:nth-child(2)'                     # 取消按钮
    BTN_CONFIRM_MAP = 'button.mapButton:nth-child(3)'                    # 确认按钮
    BTN_SAVE_MAP = '.ivu-modal-confirm-footer > button:nth-child(1)'    # 保存按钮

    # ===================== 地图列表项下的四个功能按钮（动态索引） =====================
    # 设置默认地图（按钮1）
    BTN_SET_DEFAULT = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[1]/div[1]'
    # 编辑地图（按钮4）
    BTN_EDIT_MAP = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[4]/div[1]'
    # 删除地图（使用图标类定位）
    BTN_DELETE_MAP = lambda self, index: f"(//i[contains(@class,'ico-15')])[{index}]"
    # 扩展地图（按钮7，默认占位，实际在初始化时根据 env 覆盖）
    BTN_EXPAND_MAP = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[7]/div[1]'

    # ===================== 编辑/扩展相关元素定位 =====================
    BTN_EDIT_ENTRY = "//*[text()='清除噪点']/ancestor::button[1]"        # 进入编辑（清除噪点按钮）
    BTN_SAVE_NOISE = "//*[text()='保存噪点框']/ancestor::button[1]"      # 保存噪点框按钮
    BTN_EXIT_EDIT = "//*[text()='退出']/ancestor::button[1]"             # 退出编辑按钮

    # 扩展地图弹窗相关
    BTN_EXPAND_CONFIRM = "//div[contains(@class,'ivu-modal') and .//div[contains(@class,'ivu-modal-header') and contains(.,'注意')]]//button[contains(@class,'ivu-btn-primary') and normalize-space()='确定']"   # 扩展确认按钮
    BTN_NAVIGATE_ITEM = '.navigate-item'                                 # 导航项（用于点击画布）
    BTN_SURE = '.sure'                                                   # 确认按钮
    BTN_EXPAND_CANCEL = 'button.mapButton:nth-child(2)'                  # 扩展取消按钮
    BTN_MODAL_FIRST = '.ivu-modal-confirm-footer > button:nth-child(1)'  # 模态框第一个按钮（常用于保存）

    # 通用删除确认弹窗
    BTN_CONFIRM_DELETE = "//div[contains(@class,'ivu-modal') and contains(.,'确定删除地图')]//button[contains(@class,'ivu-btn-primary') and normalize-space()='确定']"   # 删除地图确认按钮

    # 文件上传输入框（XPath）
    INPUT_UPLOAD_FILE = "//input[@type='file']"

    # ===================== 重定位（Relocate）功能元素 =====================
    BTN_RELOCATE_ENTRY = "//*[contains(text(),'运动控制')]"               # 运动控制入口
    BTN_RELOCATE_START = "//*[contains(text(),'导航模式')]"               # 导航模式按钮
    BTN_RELOCATE_CONFIRM = "(//*[contains(text(),'矫正定位')])[1]"        # 矫正定位按钮
    BTN_RELOCATE_SUBMIT = '.ivu-modal-confirm-footer > button:nth-child(2)'  # 模态框提交按钮
    BTN_RELOCATE_SAVE = '.ivu-modal-confirm-footer > button:nth-child(1)'    # 模态框保存按钮

    # ===================== 遥控模式入口 =====================
    BTN_REMOTE_MODE = "//*[contains(text(),'遥控模式')]"                  # 遥控模式按钮

    # ===================== 初始化 =====================
    def __init__(self, driver, env="2d"):
        """
        构造函数，根据环境加载差异化配置。

        :param driver: WebDriver 实例
        :param env: 环境类型，"2d" 或 "3d"
        """
        super().__init__(driver)
        self.env = env.lower()
        self.env_config = ENV_2D if self.env == "2d" else ENV_3D
        # 覆盖扩展地图按钮的定位（不同环境按钮索引可能不同）
        self.BTN_EXPAND_MAP = self.env_config["MAP_PAGE"]["BTN_EXPAND_MAP"]
        # 保存重定位坐标（屏幕拖拽起点和终点）
        self.relocate_coord = self.env_config["MAP_PAGE"]["RELOCATE_COORD"]
        # 保存上传文件列表（不同环境下文件上传顺序可能不同）
        self.upload_files = self.env_config["MAP_PAGE"]["UPLOAD_FILES"]

    # ===================== 公共方法 =====================
    def enter_remote_mode(self):
        """进入遥控模式（关闭弹窗后点击遥控模式按钮）"""
        self.close_all_modal()
        time.sleep(1)
        print("[INFO] 进入遥控模式")
        self.click_xpath(self.BTN_REMOTE_MODE)
        time.sleep(1)

    def enter_map_page(self):
        """进入地图管理页面：依次点击“任务设置” → “地图管理”"""
        self.click_xpath(self.TASK_SETTING)
        time.sleep(1)
        self.clear_highlight()
        self.click_xpath(self.BTN_MAP_ENTRY)
        time.sleep(2)

    # ===================== 获取地图数量（带重试，避免超时陷阱） =====================
    def get_map_count(self, retry=3):
        """
        获取地图列表中的地图数量（支持重试和显式等待）。

        :param retry: 最大重试次数
        :return: 地图数量（整数）
        """
        for i in range(retry):
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, self.LIST_MAPS))
                )
                elements = self.driver.find_elements(By.XPATH, self.LIST_MAPS)
                count = len(elements)
                if count > 0 or i == retry - 1:
                    return count
                time.sleep(1)
            except:
                time.sleep(1)
        return 0

    # ===================== 取消创建地图 =====================
    def cancel_create_map(self):
        """模拟“取消创建地图”流程：新建地图 → 填写名称 → 确认 → 取消 -> 验证数量不变"""
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
        """创建新地图的完整流程（使用自动化命名）"""
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
        编辑地图的标准流程（进入地图编辑 -> 清除噪点 -> 保存 -> 退出）。

        :param map_index: 地图索引（从1开始）
        """
        self.wait_xpath(self.BTN_EDIT_MAP(map_index))
        self.click_xpath(self.BTN_EDIT_MAP(map_index))
        time.sleep(3)

        self.wait_xpath(self.BTN_EDIT_ENTRY)
        self.click_xpath(self.BTN_EDIT_ENTRY)
        time.sleep(3)

        # 使用 pyautogui 在画布上打点（屏幕绝对坐标）
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
        """
        扩展地图的完整流程（点击扩展按钮 -> 确认 -> 打点 -> 取消 -> 保存）。

        :param map_index: 地图索引（从1开始）
        """
        time.sleep(2)
        self.click_xpath(self.BTN_EXPAND_MAP(map_index))
        time.sleep(10)
        self.click_xpath(self.BTN_EXPAND_CONFIRM)
        time.sleep(3)

        self.click_css(self.BTN_NAVIGATE_ITEM)
        time.sleep(2)
        self.pyautogui_click(771, 505)
        time.sleep(5)

        self.click_css(self.BTN_EXPAND_CANCEL)
        time.sleep(10)
        self.wait_css(self.BTN_MODAL_FIRST)
        time.sleep(2)
        self.click_css(self.BTN_MODAL_FIRST)
        time.sleep(5)

        self.click_css(self.BTN_SURE)
        time.sleep(10)
        self.wait_xpath(self.BTN_MAP_ENTRY)
        self.wait_css(self.BTN_MODAL_FIRST)
        time.sleep(2)
        self.click_css(self.BTN_MODAL_FIRST)

    # ===================== 删除地图 =====================
    def delete_map(self, map_index: int):
        """
        删除指定索引的地图（索引从1开始）。

        :param map_index: 要删除的地图索引
        """
        count_before = self.get_map_count()
        print(f"删除地图前数量: {count_before}")

        self.click_xpath(self.BTN_DELETE_MAP(map_index))
        time.sleep(2)

        self.wait_xpath(self.BTN_CONFIRM_DELETE)
        self.click_xpath(self.BTN_CONFIRM_DELETE)

        time.sleep(3)
        count_after = self.get_map_count()
        print(f"删除地图后数量: {count_after}")

    # ===================== 上传地图（环境差异化文件顺序） =====================
    def upload_map(self):
        """
        上传地图文件（数量通常为2个，根据环境配置的顺序依次上传）。
        上传后等待地图列表数量增加2，并断言验证。
        """
        self.close_all_modal()
        count_before = self.get_map_count()
        print(f"上传地图前数量: {count_before}")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

        for i, file_name in enumerate(self.upload_files):
            # 每次上传前重新获取文件输入框（避免元素过期）
            upload_input = self.find_xpath(self.INPUT_UPLOAD_FILE)
            file_path = os.path.join(data_dir, file_name)
            upload_input.send_keys(file_path)
            print(f"[UPLOAD] 正在上传: {file_name}")
            time.sleep(3)
            print(f"[OK] {file_name} 上传成功")

            if i < len(self.upload_files) - 1:
                time.sleep(2)  # 页面刷新间隔

        # 等待地图列表更新（最长等待15秒）
        for _ in range(30):
            count_after = self.get_map_count()
            if count_after == count_before + 2:
                break
            time.sleep(0.5)
        else:
            count_after = self.get_map_count()

        assert count_after == count_before + 2, f"上传后地图数量异常，期望{count_before+2}，实际{count_after}"
        print("[OK] 地图上传验证通过")
        time.sleep(5)

    # ===================== 设置默认地图 =====================
    def set_first_map_default(self):
        """将第一张地图设置为默认地图"""
        print("[INFO] 正在设置【第一张】地图为默认...")
        self.click_xpath(self.BTN_SET_DEFAULT(1))
        time.sleep(3)
        print("[OK] 第一张地图已设置为默认")

    def set_last_map_default(self):
        """将最后一张地图设置为默认地图"""
        total = self.get_map_count()
        print(f"当前地图总数：{total}，正在设置最后一张为默认...")
        self.click_xpath(self.BTN_SET_DEFAULT(total))
        time.sleep(3)
        print(f"[OK] 第 {total} 张地图已设置为默认")

    # ===================== 地图重定位（使用环境差异化坐标） =====================
    def relocate(self):
        """
        执行地图重定位（矫正定位）操作，拖拽地图以修正位置。
        起点和终点坐标根据环境配置（2D / 3D）自动适配。
        """
        print(f"开始矫正定位（{self.env.upper()}环境）")
        self.click_xpath(self.BTN_RELOCATE_ENTRY)
        time.sleep(3)
        self.click_xpath(self.BTN_RELOCATE_START)
        time.sleep(3)
        self.click_xpath(self.BTN_RELOCATE_CONFIRM)
        time.sleep(3)

        x1, y1, x2, y2 = self.relocate_coord
        self.pyautogui_drag(x1, y1, x2, y2)
        time.sleep(15)

        self.click_css(self.BTN_RELOCATE_SUBMIT)
        time.sleep(20)
        self.click_css(self.BTN_RELOCATE_SAVE)
        time.sleep(5)
        self.click_xpath(self.BTN_REMOTE_MODE)

    # ===================== 删除最后一张地图 =====================
    def delete_last_map(self):
        """删除最后一张地图（无参数，自动获取当前地图数量）。"""
        total = self.get_map_count()
        if total < 1:
            print("[INFO] 没有地图可删除")
            return
        print(f"当前共 {total} 张地图 → 即将删除最后一张")
        self.delete_map(total)