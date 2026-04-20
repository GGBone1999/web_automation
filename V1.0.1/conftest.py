import logging
import time
import sys
from pathlib import Path

# ====================== 日志基础配置 ======================
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 创建日志目录
logs_dir = Path("reports/logs")
logs_dir.mkdir(parents=True, exist_ok=True)
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"test_run_{timestamp}.log"

# 清空根 logger 原有处理器，避免冲突
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.setLevel(logging.INFO)

# 文件输出 handler
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# 控制台输出 handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# 添加处理器
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# ====================== 安全重定向 print ======================
original_print = print

def redirected_print(*args, **kwargs):
    try:
        msg = " ".join(str(arg) for arg in args)
        logging.info(msg)
    except Exception:
        pass

# 全局安全替换 print（解决 __builtins__ 报错）
print = redirected_print

# 启动日志
print("==================================================")
print("✅ 自动化测试日志系统已启动")
print(f"📄 日志文件：{log_file}")
print("==================================================")