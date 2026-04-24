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
    """基础页面类，封装通用操作"""
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait_time = 3          # 默认显式等待超时（秒），可根据需要调整
        pyautogui.FAILSAFE = True

    # ===================== 等待 =====================
    def wait_xpath(self, xpath: str, timeout=None):
        wait_time = timeout if timeout is not None else self.wait_time
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            # 移除额外的 sleep 0.5，避免不必要的延迟
        except TimeoutException:
            print(f"⚠️ 超时未找到元素: {xpath}")

    def wait_css(self, css: str, timeout=None):
        wait_time = timeout if timeout is not None else self.wait_time
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css))
            )
        except TimeoutException:
            print(f"⚠️ 超时未找到元素: {css}")

    def find_xpath(self, xpath: str, timeout=None):
        """查找元素（自动等待可见）"""
        self.wait_xpath(xpath, timeout)
        return self.driver.find_element(By.XPATH, xpath)

    def find_css(self, css: str, timeout=None):
        self.wait_css(css, timeout)
        return self.driver.find_element(By.CSS_SELECTOR, css)

    # ===================== 点击（带高亮 + 性能优化） =====================
    def click_xpath(self, xpath: str, retry: int = 2, wait_time: int = None):
        """
        点击 XPath 定位的元素，保留高亮功能。
        - 高亮：清除所有之前的 .highlight-click，为当前元素添加红色边框。
        - 性能：使用纯 JS 隐藏遮罩，减少重试次数，缩短默认超时。
        """
        if wait_time is None:
            wait_time = self.wait_time

        # 清除所有旧高亮
        self.driver.execute_script("""
            document.querySelectorAll('.highlight-click').forEach(el => {
                el.style.border = '';
                el.classList.remove('highlight-click');
            });
        """)

        for attempt in range(retry):
            try:
                # 快速隐藏遮罩（纯 JS，不触发隐式等待）
                self._close_visible_mask_fast()

                # 等待元素可点击
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                # 滚动到可视区域
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.2)  # 短暂等待滚动完成

                # 高亮当前元素
                self.driver.execute_script("""
                    arguments[0].style.border = '2px solid red';
                    arguments[0].classList.add('highlight-click');
                """, element)

                # 尝试正常点击
                element.click()
                time.sleep(0.2)  # 点击后短暂间隔，可酌情保留
                return True

            except ElementClickInterceptedException:
                # 元素被遮挡时快速清理遮罩并重试
                self._close_visible_mask_fast()
                time.sleep(0.3)
                continue

            except (StaleElementReferenceException, TimeoutException) as e:
                print(f"⚠️ XPath 点击失败 (尝试 {attempt+1}/{retry}): {xpath[:80]} => {str(e)[:50]}")
                if attempt == retry - 1:
                    # 最后尝试 JS 点击
                    try:
                        element = self.driver.find_element(By.XPATH, xpath)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.2)
                        return True
                    except Exception as final_e:
                        print(f"❌ XPath 点击彻底失败: {xpath} => {final_e}")
                        raise
                time.sleep(0.5)
        return False

    def click_css(self, css: str, retry: int = 2, wait_time: int = None):
        if wait_time is None:
            wait_time = self.wait_time

        # 清除旧高亮（为了统一体验，CSS点击也保持相同高亮逻辑）
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
                print(f"⚠️ CSS 点击失败 (尝试 {attempt+1}/{retry}): {css[:80]} => {str(e)[:50]}")
                if attempt == retry - 1:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, css)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.2)
                        return True
                    except Exception as final_e:
                        print(f"❌ CSS 点击彻底失败: {css} => {final_e}")
                        raise
                time.sleep(0.5)
        return False

    # ===================== 输入 =====================
    def input_xpath(self, xpath: str, text: str):
        try:
            elem = self.find_xpath(xpath)
            elem.clear()
            elem.send_keys(text)
        except Exception as e:
            print(f"⚠️ XPath输入失败: {xpath} => {e}")

    def input_css(self, css: str, text: str):
        try:
            elem = self.find_css(css)
            elem.clear()
            elem.send_keys(text)
        except Exception as e:
            print(f"⚠️ CSS输入失败: {css} => {e}")

    def get_element_text(self, xpath: str) -> str:
        try:
            return self.find_xpath(xpath).text
        except Exception:
            return ""

    def get_element_count(self, xpath: str) -> int:
        try:
            return len(self.driver.find_elements(By.XPATH, xpath))
        except Exception:
            return 0

    # ===================== 鼠标操作 =====================
    def pyautogui_click(self, x: int, y: int):
        pyautogui.click(x=x, y=y)

    def pyautogui_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1):
        pyautogui.mouseDown(start_x, start_y, button='left')
        pyautogui.moveTo(end_x, end_y, duration=duration)
        pyautogui.mouseUp(button='left')

    def switch_to_default_frame(self):
        self.driver.switch_to.default_content()

    # ===================== 关闭可见遮罩（纯 JS，极速） =====================
    def _close_visible_mask_fast(self):
        """仅通过 JS 隐藏遮罩，不调用 find_elements，避免隐式等待"""
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

    # ===================== 关闭可见弹窗（保持原有移除逻辑，但可选） =====================
    def close_all_modal(self):
        """移除可见弹窗（保留原功能）"""
        try:
            self.driver.execute_script("""
                document.querySelectorAll('.ivu-modal-wrap, .ivu-modal').forEach(m => {
                    if (m.offsetParent !== null && m.style.display !== 'none') {
                        m.remove();
                    }
                });
            """)
            print("✅ 已清理【可见】异常弹窗")
        except Exception as e:
            print(f"⚠️ 关闭弹窗失败: {e}")

    # 保留旧方法名以兼容现有代码（如果你有其他地方调用 _close_visible_mask，可以重定向）
    def _close_visible_mask(self):
        self._close_visible_mask_fast()
    
    def clear_highlight(self):
        self.driver.execute_script("""
        document.querySelectorAll('.highlight-click').forEach(el => {
            el.style.border = '';
            el.classList.remove('highlight-click');
        });
    """)