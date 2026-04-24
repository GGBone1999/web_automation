import time
import os
from utils.time_tools import dt_strftime
from base.base_page import BasePage
from selenium.webdriver.common.action_chains import ActionChains

class MapPage(BasePage):
    """
    地图管理页面类
    功能：新建、编辑、拓展、删除、上传、设置默认、重定位地图、遥控模式
    """

    # ===================== 基础定位 =====================
    BTN_MAP_ENTRY = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div'
    LIST_MAPS = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div'
    BTN_NEW_MAP = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[1]/button'
    INPUT_MAP_NAME = '/html/body/div[12]/div[2]/div/div/div[2]/div/div/input'
    BTN_MAP_CONFIRM = '/html/body/div[12]/div[2]/div/div/div[3]/div/button[2]/span'
    BTN_CANCEL_MAP = 'button.mapButton:nth-child(2)'
    BTN_CONFIRM_MAP = 'button.mapButton:nth-child(3)'
    BTN_SAVE_MAP = '.ivu-modal-confirm-footer > button:nth-child(1)'

    # ===================== 编辑地图 =====================
    BTN_EDIT_MAP = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[4]/div[1]'
    BTN_EDIT_ENTRY = '.navi-map-bottom-status > button:first-child'

    # ===================== 拓展地图 =====================
    BTN_EXPAND_MAP = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[6]/div[1]'
    BTN_EXPAND_CONFIRM = '/html/body/div[24]/div[2]/div/div/div[3]/div/button'
    BTN_NAVIGATE_ITEM = '.navigate-item'
    BTN_SURE = '.sure'

    # ===================== 删除地图 =====================
    BTN_DELETE_MAP = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[5]'
    BTN_CONFIRM_DELETE = '.ivu-modal-confirm-footer > button:nth-child(2)'

    # ===================== 上传地图 =====================
    INPUT_UPLOAD_FILE = '.ivu-upload-input'

    # ===================== 默认地图 =====================
    BTN_SET_DEFAULT = lambda self, index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[1]/div[1]'
    BTN_RESET_DEFAULT = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/p[2]/div[1]'

    # ===================== 重定位 =====================
    BTN_RELOCATE_ENTRY = '/html/body/div[1]/div/div[1]/div/div[1]/div[1]'
    BTN_RELOCATE_START = '/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div'
    BTN_RELOCATE_CONFIRM = '/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div[2]/div/div[2]/div/div[1]/button'
    BTN_RELOCATE_SUBMIT = '.ivu-modal-confirm-footer > button:nth-child(2)'
    BTN_RELOCATE_SAVE = '.ivu-modal-confirm-footer > button:nth-child(1)'
    BTN_RELOCATE_BACK = '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div'

    # ===================== 【新增】遥控模式 =====================
    # 你提供的遥控模式定位
    BTN_REMOTE_MODE = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div"

    # ===================== 初始化 =====================
    def __init__(self, driver):
        super().__init__(driver)

    # ===================== 【新增】进入遥控模式 → 跳转到任务设置 =====================
    def enter_remote_mode(self):
        """
        新增功能：
        1. 点击【遥控模式】按钮
        2. 进入遥控模式页面
        """
        print("👉 进入遥控模式")
        self.click_xpath(self.BTN_REMOTE_MODE)
        time.sleep(1)

    # ===================== 进入任务设置默认地图管理页 =====================
    def enter_map_page(self):
        """进入任务设置默认地图管理页"""
        self.close_all_modal()
        time.sleep(1)
        self.click_xpath(self.BTN_MAP_ENTRY)
        time.sleep(2)

    # ===================== 获取地图数量 =====================
    def get_map_count(self) -> int:
        """获取当前地图总数"""
        return self.get_element_count(self.LIST_MAPS)

    # ===================== 取消建图 =====================
    def cancel_create_map(self):
        """取消新建地图流程"""
        self.enter_remote_mode()
        time.sleep(1)
        self.enter_map_page()
        count_before = self.get_map_count()
        print(f"取消建图前数量: {count_before}")

        self.click_xpath(self.BTN_NEW_MAP)
        time.sleep(3)
        self.input_xpath(self.INPUT_MAP_NAME, dt_strftime("%Y%m%d%H%M%S"))
        self.click_xpath(self.BTN_MAP_CONFIRM)
        time.sleep(20)

        self.wait_css(self.BTN_CANCEL_MAP)
        self.click_css(self.BTN_CANCEL_MAP)

        count_after = self.get_map_count()
        print(f"取消建图后数量: {count_after}")
        # assert count_before == count_after, "取消建图后数量异常"
        time.sleep(5)

    # ===================== 新建地图 =====================
    def create_new_map(self, map_name: str = "自动化地图"):
        """新建地图并保存"""
        count_before = self.get_map_count()
        print(f"新建地图前数量: {count_before}")

        self.click_xpath(self.BTN_NEW_MAP)
        time.sleep(2)
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
        # assert count_after == count_before + 1, "新建地图数量异常"
        time.sleep(7)

    # ===================== 编辑地图 =====================
    def edit_map(self, map_index: int):
        """编辑地图：绘制噪点并保存退出"""
        # 点击编辑按钮
        self.click_xpath(self.BTN_EDIT_MAP(map_index))
        time.sleep(3)

        # 进入编辑模式
        self.wait_css(self.BTN_EDIT_ENTRY)
        self.click_css(self.BTN_EDIT_ENTRY)
        time.sleep(3)

        # 画布点击三个点
        self.pyautogui_click(771, 505)
        time.sleep(1)
        self.pyautogui_click(838, 669)
        time.sleep(1)
        self.pyautogui_click(993, 506)
        time.sleep(2)

        # 保存噪点框
        try:
            self.click_xpath("//*[contains(text(), '保存噪点框')]")
        except:
            self.click_css("div[class*='btn']:last-child")
        time.sleep(3)

        # 退出编辑
        try:
            self.click_xpath("//*[text()='退出']")
        except:
            pass
        time.sleep(3)

    # ===================== 拓展地图 =====================
    def expand_map(self, map_index: int):
        """拓展地图（严格按你的用例流程）"""
        # 点击拓展按钮
        self.click_xpath(self.BTN_EXPAND_MAP(map_index))
        time.sleep(1)

        # 点击拓展弹窗确认
        self.wait_xpath(self.BTN_EXPAND_CONFIRM)
        self.click_xpath(self.BTN_EXPAND_CONFIRM)
        time.sleep(5)

        # 点击导航项
        self.click_css(self.BTN_NAVIGATE_ITEM)

        # 画布点击
        self.pyautogui_click(771, 505)
        time.sleep(5)

        # 取消绘制
        self.click_css('button.mapButton:nth-child(2)')

        # 确认保存
        self.wait_css('.ivu-modal-confirm-footer > button:nth-child(1)')
        self.click_css('.ivu-modal-confirm-footer > button:nth-child(1)')
        time.sleep(5)

        # 提示确定
        self.click_css('.sure')

        # 返回地图页并确认
        self.wait_xpath(self.BTN_MAP_ENTRY)
        self.wait_css('.ivu-modal-confirm-footer > button:nth-child(1)')
        self.click_css('.ivu-modal-confirm-footer > button:nth-child(1)')

    # ===================== 删除地图 =====================
    def delete_map(self, map_index: int):
        """
        删除地图
        :param map_index: 地图序号（从上到下 1、2、3...）
        """
        count_before = self.get_map_count()
        print(f"删除地图前数量: {count_before}")

        # 点击第 map_index 个地图的删除按钮
        self.click_xpath(self.BTN_DELETE_MAP(map_index))
        time.sleep(1)

        # 确认删除
        self.click_css(self.BTN_CONFIRM_DELETE)
        time.sleep(3)

        count_after = self.get_map_count()
        print(f"删除地图后数量: {count_after}")
        # assert count_after == count_before - 1, "删除地图数量异常"

    # ===================== 上传地图 =====================
    def upload_map(self):
        """上传地图（失败即抛出异常，不允许静默失败）"""
        self.close_all_modal()
        count_before = self.get_map_count()
        print(f"上传地图前数量: {count_before}")

        # 获取项目根目录和 data 文件夹
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

        # 上传第一个地图文件
        file1_path = os.path.join(data_dir, "map1.json")
        upload_input = self.find_css(self.INPUT_UPLOAD_FILE)   # 获取上传控件
        upload_input.send_keys(file1_path)
        time.sleep(3)   # 等待上传完成（可优化为显式等待）
        print("✅ map1.json 上传成功")
        time.sleep(1)

        # 上传第二个地图文件（重新获取元素，避免状态变化）
        file2_path = os.path.join(data_dir, "map2.json")
        # 注意：如果同一个 input 支持多文件选择，可以直接 send_keys 两次；
        # 但为防止追加或替换问题，重新定位元素更稳妥
        upload_input = self.find_css(self.INPUT_UPLOAD_FILE)
        upload_input.send_keys(file2_path)
        time.sleep(3)
        print("✅ map2.json 上传成功")
        time.sleep(1)

        # 验证地图数量是否增加 2
        count_after = self.get_map_count()
        assert count_after == count_before + 2, \
            f"上传后地图数量异常，期望 {count_before + 2}，实际 {count_after}"
        print("✅ 地图上传验证通过")
        time.sleep(5)

    # ===================== 设置默认地图 =====================
    def set_first_map_default(self):
        """设置 第一张 地图为默认地图"""
        print("✅ 正在设置【第一张】地图为默认...")
        self.click_xpath(self.BTN_SET_DEFAULT(1))
        time.sleep(3)
        print("✅ 第一张地图已设置为默认")

    # ===================== 🔥 新增：设置最后一张地图为默认地图 =====================
    def set_last_map_default(self):
        """自动设置最后一张地图为默认地图"""
        total = self.get_map_count()
        print(f"当前地图总数：{total}，正在设置最后一张为默认...")
        self.click_xpath(self.BTN_SET_DEFAULT(total))
        time.sleep(3)
        print(f"✅ 第 {total} 张地图已设置为默认")

    # ===================== 重定位 =====================
    def relocate(self):
        """重定位流程"""
        print("开始重定位")
        self.click_xpath(self.BTN_RELOCATE_ENTRY)
        time.sleep(3)
        self.click_xpath(self.BTN_RELOCATE_START)
        time.sleep(3)
        self.click_xpath(self.BTN_RELOCATE_CONFIRM)
        time.sleep(3)

        self.pyautogui_drag(706, 467, 706, 462)
        time.sleep(15)

        self.click_css(self.BTN_RELOCATE_SUBMIT)
        time.sleep(20)
        self.click_css(self.BTN_RELOCATE_SAVE)
        time.sleep(5)
        self.click_xpath(self.BTN_RELOCATE_BACK)

    def delete_last_map(self):
        """自动删除 最后一张 地图（无需传参）"""
        total = self.get_map_count()
        if total < 1:
            print("[表情] 没有地图可删除")
            return
    
        print(f"当前共 {total} 张地图 → 即将删除【最后一张】（第 {total} 张）")
        self.delete_map(total)