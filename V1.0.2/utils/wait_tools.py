import unittest
from unittest import TestCase
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from utils.times import timestamp, dt_strftime, running_time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException



def wait_css(css):
    wait = WebDriverWait(self.driver, 60)
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
    sleep(3)
    print('执行等待')


def wait_xpath(xpath):
    wait = WebDriverWait(self.driver, 60)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    sleep(3)
    print('执行等待')

