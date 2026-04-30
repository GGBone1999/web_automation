from time import sleep
import pyautogui

screen_width, screen_height = pyautogui.size()


for i in range(100):
    current_x, current_y = pyautogui.position()
    sleep(0.1)
    print(current_x, current_y)