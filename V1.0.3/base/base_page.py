# -*- coding: utf-8 -*-
"""
基础页面交互模块

提供页面元素操作、等待、点击、输入、鼠标模拟、弹窗清理等通用方法。
所有方法基于 Selenium WebDriver 和 pyautogui 实现。
"""

import time
import pyautogui
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)


class BasePage:
    """基础页面类，封装浏览器操作的通用行为，所有页面类可继承此类。"""

    def __init__(self, driver: webdriver.Chrome):
        """
        初始化页面对象。

        :param driver: Chrome WebDriver 实例
        """
        self.driver = driver
        self.wait_time = 3          # 默认显式等待超时（秒），可随时调整
        pyautogui.FAILSAFE = True   # 启用 pyautogui 安全模式，将鼠标移至屏幕左上角可中断操作

    # ===================== 等待元素可见 =====================
    def wait_xpath(self, xpath: str, timeout=None):
        """
        等待 XPath 对应的元素变为可见。

        :param xpath: 元素的 XPath 表达式
        :param timeout: 等待超时秒数，默认使用 self.wait_time
        """
        wait_time = timeout if timeout is not None else self.wait_time
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
        except TimeoutException:
            print(f"[WARN] 超时未找到元素: {xpath}")

    def wait_css(self, css: str, timeout=None):
        """
        等待 CSS 选择器对应的元素变为可见。

        :param css: CSS 选择器字符串
        :param timeout: 等待超时秒数，默认使用 self.wait_time
        """
        wait_time = timeout if timeout is not None else self.wait_time
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css))
            )
        except TimeoutException:
            print(f"[WARN] 超时未找到元素: {css}")

    # ===================== 查找元素 =====================
    def find_xpath(self, xpath: str, timeout=None):
        """
        查找 XPath 对应的元素（自动等待可见后返回）。

        :param xpath: 元素的 XPath 表达式
        :param timeout: 等待超时秒数
        :return: WebElement 对象
        """
        self.wait_xpath(xpath, timeout)
        return self.driver.find_element(By.XPATH, xpath)

    def find_css(self, css: str, timeout=None):
        """
        查找 CSS 选择器对应的元素（自动等待可见后返回）。

        :param css: CSS 选择器字符串
        :param timeout: 等待超时秒数
        :return: WebElement 对象
        """
        self.wait_css(css, timeout)
        return self.driver.find_element(By.CSS_SELECTOR, css)

    # ===================== 点击操作（带高亮与遮挡处理） =====================
    def click_xpath(self, xpath: str, retry: int = 2, wait_time: int = None):
        """
        点击 XPath 定位的元素，带有重试、遮挡清理和高亮显示功能。

        :param xpath: 元素的 XPath 表达式
        :param retry: 失败后的最大重试次数
        :param wait_time: 等待元素可点击的超时秒数，默认使用 self.wait_time
        :return: 点击是否成功（bool）
        """
        if wait_time is None:
            wait_time = self.wait_time

        # 清除所有现有高亮标记
        self.driver.execute_script("""
            document.querySelectorAll('.highlight-click').forEach(el => {
                el.style.border = '';
                el.classList.remove('highlight-click');
            });
        """)

        for attempt in range(retry):
            try:
                # 用 JavaScript 快速隐藏遮挡层（避免隐式等待）
                self._close_visible_mask_fast()

                # 等待元素可点击
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                # 滚动到视图中央
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.2)  # 等待滚动稳定

                # 高亮当前元素（红色边框）
                self.driver.execute_script("""
                    arguments[0].style.border = '2px solid red';
                    arguments[0].classList.add('highlight-click');
                """, element)

                # 尝试正常点击
                element.click()
                time.sleep(0.2)  # 点击后动作缓冲
                return True

            except ElementClickInterceptedException:
                # 点击被遮挡，再次清理遮罩后重试
                self._close_visible_mask_fast()
                time.sleep(0.3)
                continue

            except (StaleElementReferenceException, TimeoutException) as e:
                print(f"[WARN] XPath 点击失败 (尝试 {attempt+1}/{retry}): {xpath[:80]} => {str(e)[:50]}")
                if attempt == retry - 1:
                    # 最后一次尝试：使用 JavaScript 强制点击
                    try:
                        element = self.driver.find_element(By.XPATH, xpath)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.2)
                        return True
                    except Exception as final_e:
                        print(f"[ERROR] XPath 点击彻底失败: {xpath} => {final_e}")
                        raise
                time.sleep(0.5)
        return False

    def click_css(self, css: str, retry: int = 2, wait_time: int = None):
        """
        点击 CSS 选择器定位的元素，带有重试、遮挡清理和高亮显示功能。

        :param css: CSS 选择器字符串
        :param retry: 失败后的最大重试次数
        :param wait_time: 等待元素可点击的超时秒数，默认使用 self.wait_time
        :return: 点击是否成功（bool）
        """
        if wait_time is None:
            wait_time = self.wait_time

        # 清除所有高亮标记
        self.driver.execute_script("""
            document.querySelectorAll('.highlight-click').forEach(el => {
                el.style.border = '';
                el.classList.remove('highlight-click');
            });
        """)

        for attempt in range(retry):
            try:
                self._close_visible_mask_fast()
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, css))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.2)
                self.driver.execute_script("""
                    arguments[0].style.border = '2px solid red';
                    arguments[0].classList.add('highlight-click');
                """, element)
                element.click()
                time.sleep(0.2)
                return True

            except ElementClickInterceptedException:
                self._close_visible_mask_fast()
                time.sleep(0.3)
                continue

            except (StaleElementReferenceException, TimeoutException) as e:
                print(f"[WARN] CSS 点击失败 (尝试 {attempt+1}/{retry}): {css[:80]} => {str(e)[:50]}")
                if attempt == retry - 1:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, css)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.2)
                        return True
                    except Exception as final_e:
                        print(f"[ERROR] CSS 点击彻底失败: {css} => {final_e}")
                        raise
                time.sleep(0.5)
        return False

    # ===================== 输入操作 =====================
    def input_xpath(self, xpath: str, text: str):
        """
        向 XPath 定位的元素输入文本（先清空再输入）。

        :param xpath: 元素的 XPath 表达式
        :param text: 要输入的文本内容
        """
        try:
            elem = self.find_xpath(xpath)
            elem.clear()
            elem.send_keys(text)
        except Exception as e:
            print(f"[WARN] XPath输入失败: {xpath} => {e}")

    def input_css(self, css: str, text: str):
        """
        向 CSS 选择器定位的元素输入文本（先清空再输入）。

        :param css: CSS 选择器字符串
        :param text: 要输入的文本内容
        """
        try:
            elem = self.find_css(css)
            elem.clear()
            elem.send_keys(text)
        except Exception as e:
            print(f"[WARN] CSS输入失败: {css} => {e}")

    def get_element_text(self, xpath: str) -> str:
        """
        获取 XPath 定位元素的文本内容。

        :param xpath: 元素的 XPath 表达式
        :return: 元素的文本，若失败则返回空字符串
        """
        try:
            return self.find_xpath(xpath).text
        except Exception:
            return ""

    def get_element_count(self, xpath: str) -> int:
        """
        统计 XPath 匹配的元素数量（常用于判断列表项个数）。

        :param xpath: 元素的 XPath 表达式
        :return: 匹配到的元素个数
        """
        try:
            return len(self.driver.find_elements(By.XPATH, xpath))
        except Exception:
            return 0

    # ===================== 鼠标模拟（pyautogui） =====================
    def pyautogui_click(self, x: int, y: int):
        """
        使用 pyautogui 在屏幕绝对坐标 (x, y) 处模拟鼠标左键点击。

        :param x: 屏幕 X 坐标
        :param y: 屏幕 Y 坐标
        """
        pyautogui.click(x=x, y=y)

    def pyautogui_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1):
        """
        使用 pyautogui 模拟鼠标拖拽：从起点按着左键拖动到终点。

        :param start_x: 起点 X 坐标
        :param start_y: 起点 Y 坐标
        :param end_x: 终点 X 坐标
        :param end_y: 终点 Y 坐标
        :param duration: 拖拽持续时间（秒）
        """
        pyautogui.mouseDown(start_x, start_y, button='left')
        pyautogui.moveTo(end_x, end_y, duration=duration)
        pyautogui.mouseUp(button='left')

    def switch_to_default_frame(self):
        """切换回页面的顶层默认框架（用于处理 iframe 嵌套场景）。"""
        self.driver.switch_to.default_content()

    # ===================== 辅助：清理遮挡层 =====================
    def _close_visible_mask_fast(self):
        """
        快速通过 JavaScript 隐藏页面上常见的可见遮罩层（如模态框背景、loading 遮罩等）。
        此方法不调用 find_elements，避免触发 Selenium 隐式等待，提高执行速度。
        """
        try:
            self.driver.execute_script("""
                document.querySelectorAll('.ivu-modal-mask, .modal-backdrop, .overlay, .mask').forEach(el => {
                    if (el.offsetParent !== null && el.style.display !== 'none') {
                        el.style.display = 'none';
                    }
                });
            """)
        except Exception:
            pass

    def close_all_modal(self):
        """移除页面中可见的弹出模态框（直接 DOM 移除）。"""
        try:
            self.driver.execute_script("""
                document.querySelectorAll('.ivu-modal-wrap, .ivu-modal').forEach(m => {
                    if (m.offsetParent !== null && m.style.display !== 'none') {
                        m.remove();
                    }
                });
            """)
            print("[INFO] 已清理可见异常弹窗")
        except Exception as e:
            print(f"[WARN] 关闭弹窗失败: {e}")

    def _close_visible_mask(self):
        """
        兼容旧方法名，实际调用快速遮罩隐藏方法 _close_visible_mask_fast()。
        若有旧的测试用例调用此方法，可继续正常工作。
        """
        self._close_visible_mask_fast()

    def clear_highlight(self):
        """清除所有元素上由高亮操作留下的红色边框和 'highlight-click' 类。"""
        self.driver.execute_script("""
            document.querySelectorAll('.highlight-click').forEach(el => {
                el.style.border = '';
                el.classList.remove('highlight-click');
            });
        """)