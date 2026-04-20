import time
import pyautogui
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException

class BasePage:
    """基础页面类，封装通用操作"""
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait_time = 8

    # ===================== 修复支持 timeout 参数 =====================
    def wait_xpath(self, xpath: str, timeout=None):
        wait_time = timeout if timeout is not None else self.wait_time
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            time.sleep(0.5)
        except TimeoutException:
            print(f"⚠️ 超时未找到元素: {xpath}")

    def wait_css(self, css: str, timeout=None):
        wait_time = timeout if timeout is not None else self.wait_time
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css))
            )
            time.sleep(0.5)
        except TimeoutException:
            print(f"⚠️ 超时未找到元素: {css}")

    def find_xpath(self, xpath: str):
        self.wait_xpath(xpath)
        return self.driver.find_element(By.XPATH, xpath)

    def find_css(self, css: str):
        self.wait_css(css)
        return self.driver.find_element(By.CSS_SELECTOR, css)

    def click_xpath(self, xpath: str, retry: int = 3):
        self.driver.execute_script("""
            document.querySelectorAll('.highlight-click').forEach(el => {
                el.style.border = '';
                el.classList.remove('highlight-click');
            });
        """)

        for attempt in range(retry):
            try:
                element = WebDriverWait(self.driver, self.wait_time).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.3)

                self.driver.execute_script("""
                    arguments[0].style.border = '2px solid red';
                    arguments[0].classList.add('highlight-click');
                """, element)

                ActionChains(self.driver).move_to_element(element).click().perform()
                time.sleep(0.5)
                return True

            except ElementClickInterceptedException:
                print(f"⚠️ XPath 元素被遮挡，尝试移除遮罩: {xpath}")
                self.driver.execute_script("""
                 document.querySelectorAll('.ivu-modal-mask, .modal-backdrop, .mask').forEach(el => el.style.display='none');
                """)
                time.sleep(0.5)
                continue

            except (StaleElementReferenceException, Exception) as e:
                print(f"⚠️ XPath 点击失败 (尝试 {attempt+1}/{retry}): {xpath} => {str(e)[:100]}")
                if attempt == retry - 1:
                    try:
                        element = self.driver.find_element(By.XPATH, xpath)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.5)
                        return True
                    except Exception as final_e:
                        print(f"❌ XPath 点击彻底失败: {xpath} => {final_e}")
                        raise
                time.sleep(1)
        return False

    def click_css(self, css: str, retry: int = 3):
        for attempt in range(retry):
            try:
                element = WebDriverWait(self.driver, self.wait_time).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, css))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.3)

                ActionChains(self.driver).move_to_element(element).click().perform()
                time.sleep(0.5)
                return True

            except ElementClickInterceptedException:
                print(f"⚠️ CSS 元素被遮挡，尝试移除遮罩: {css}")
                self.driver.execute_script("""
                    document.querySelectorAll('.ivu-modal-mask, .modal-backdrop, .mask').forEach(el => el.style.display='none');
                """)
                time.sleep(0.5)
                continue

            except (StaleElementReferenceException, Exception) as e:
                print(f"⚠️ CSS 点击失败 (尝试 {attempt+1}/{retry}): {css} => {str(e)[:100]}")
                if attempt == retry - 1:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, css)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.5)
                        return True
                    except Exception as final_e:
                        print(f"❌ CSS 点击彻底失败: {css} => {final_e}")
                        raise
                time.sleep(1)
        return False

    def input_xpath(self, xpath: str, text: str):
        try:
            elem = self.find_xpath(xpath)
            elem.clear()
            elem.send_keys(text)
        except:
            pass

    def input_css(self, css: str, text: str):
        elem = self.find_css(css)
        elem.clear()
        elem.send_keys(text)

    def get_element_text(self, xpath: str) -> str:
        try:
            return self.find_xpath(xpath).text
        except:
            return ""

    def get_element_count(self, xpath: str) -> int:
        return len(self.driver.find_elements(By.XPATH, xpath))

    def pyautogui_click(self, x: int, y: int):
        pyautogui.click(x=x, y=y)

    def pyautogui_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1):
        pyautogui.mouseDown(start_x, start_y, button='left')
        pyautogui.moveTo(end_x, end_y, duration=duration)
        pyautogui.mouseUp(button='left')

    def switch_to_default_frame(self):
        self.driver.switch_to.default_content()

    def close_all_modal(self):
        try:
            js = """
            document.querySelectorAll('.ivu-modal-wrap, .ivu-modal-mask, .modal-backdrop, .modal').forEach(e=>e.remove());
            """
            self.driver.execute_script(js)
            print("✅ 已清理所有弹窗遮挡")
        except:
            pass