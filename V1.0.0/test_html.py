# -*- coding: utf-8 -*-
from selenium import webdriver
import unittest
import HTMLTestRunner  # 导入手动下载的模块
import time


# 定义一个测试类，继承自 unittest.TestCase
class BaiduSearchTest(unittest.TestCase):
    """百度搜索测试用例"""

    def setUp(self):
        """每个测试方法执行前运行"""
        self.driver = webdriver.Chrome()  # 确保chromedriver在PATH中
        self.driver.implicitly_wait(10)
        self.base_url = "http://www.baidu.com"

    def test_search_selenium(self):
        """测试搜索关键词'selenium'"""
        driver = self.driver
        driver.get(self.base_url)
        # 验证页面标题
        self.assertIn("百度一下", driver.title)
        # 在搜索框中输入"selenium"
        search_box = driver.find_element_by_id("kw")
        search_box.clear()
        search_box.send_keys("selenium")
        # 点击“百度一下”按钮
        driver.find_element_by_id("su").click()
        # 等待一下以便观察结果，实际使用时可根据需要调整或使用显式等待
        time.sleep(2)
        # 验证搜索结果页面的标题
        self.assertIn("selenium", driver.title.lower())

    def tearDown(self):
        """每个测试方法执行后运行"""
        self.driver.quit()


if __name__ == '__main__':
    # 1. 创建一个测试套件
    test_suite = unittest.TestSuite()
    # 将测试用例添加到套件中
    test_suite.addTest(BaiduSearchTest('test_search_selenium'))

    # 2. 定义报告文件路径，使用时间戳防止覆盖
    report_time = time.strftime("%Y%m%d_%H%M%S")
    report_filename = f'report_{report_time}.html'

    # 3. 以二进制写模式打开报告文件
    with open(report_filename, 'wb') as fp:
        # 4. 初始化HTMLTestRunner
        runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,  # 指定报告写入的文件流
            title='百度搜索测试报告',  # 报告主标题
            description='测试用例执行情况：'  # 报告副标题
        )
        # 5. 运行测试套件并生成报告
        runner.run(test_suite)

    print(f"HTML测试报告已生成：{report_filename}")
