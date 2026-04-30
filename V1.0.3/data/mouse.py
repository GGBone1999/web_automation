# -*- coding: utf-8 -*-
"""
获取鼠标当前屏幕坐标的辅助脚本

用于快速获取鼠标在屏幕上的坐标，常用于配置自动化测试中的点击坐标参数。
"""

import pyautogui      # 导入鼠标键盘自动化库
import time           # 导入时间控制模块

time.sleep(5)         # 暂停5秒，给用户移动鼠标到目标位置的时间

print(pyautogui.position())   # 获取并打印鼠标指针当前在屏幕上的坐标 (x, y)