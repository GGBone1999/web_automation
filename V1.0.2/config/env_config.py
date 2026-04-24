# config/env_config.py
# 仅用于 2D / 3D 雷达环境差异化配置
# 无任何项目基础配置、无URL、无冲突内容

ENV_2D = {
    "MAP_PAGE": {
        "BTN_EXPAND_MAP": lambda index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[6]/div[1]',
        "RELOCATE_COORD": (706, 467, 706, 462),
        "UPLOAD_FILES": ["3Dmap.json", "2Dmap.json"]
    }
}

ENV_3D = {
    "MAP_PAGE": {
        "BTN_EXPAND_MAP": lambda index: f'/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[{index}]/div/div[2]/p[2]/div[7]/div[1]',
        "RELOCATE_COORD": (504, 827, 504, 830),
        "UPLOAD_FILES": ["2Dmap.json", "3Dmap.json"]
    }
}