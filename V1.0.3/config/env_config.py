# -*- coding: utf-8 -*-
"""
环境差异化配置文件

用于 2D 和 3D 雷达环境下的页面元素定位、操作坐标、上传文件等差异化配置。
注意：本文件不包含项目基础配置（如 URL、超时时间等），仅用于环境切换。
"""

# ==================== 2D 环境配置 ====================
ENV_2D = {
    "MAP_PAGE": {
        # 地图列表中，展开第 index 个地图的按钮 XPath 表达式（动态索引）
        "BTN_EXPAND_MAP": lambda index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[6]/div[1]',
        # 重新定位操作的屏幕坐标：(起始X, 起始Y, 终点X, 终点Y)
        "RELOCATE_COORD": (706, 467, 706, 462),
        # 上传地图时使用的文件列表（按顺序上传）
        "UPLOAD_FILES": ["3Dmap.json", "2Dmap.json"]
    }
}

# ==================== 3D 环境配置 ====================
ENV_3D = {
    "MAP_PAGE": {
        # 地图列表中，展开第 index 个地图的按钮 XPath 表达式（动态索引，与 2D 环境不同）
        "BTN_EXPAND_MAP": lambda index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[7]/div[1]',
        # 重新定位操作的屏幕坐标（3D 环境下坐标不同）
        "RELOCATE_COORD": (504, 827, 504, 830),
        # 上传地图时使用的文件列表（顺序与 2D 环境相反）
        "UPLOAD_FILES": ["2Dmap.json", "3Dmap.json"]
    }
}