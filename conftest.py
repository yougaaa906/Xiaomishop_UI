import os
import sys
import urllib3
urllib3.Timeout.DEFAULT_TIMEOUT = urllib3.Timeout(total=10)

# 获取项目根目录
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# 导入核心模块
import pytest
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ========== 恢复config.py导入（关键：你确认会上传该文件） ==========
from config.config import TIMEOUT, TEST_URL, CHROME_DRIVER_PATH

# 定义日志/截图路径
LOG_DIR = os.path.join(project_path, "logs")
SCREENSHOTS_DIR = os.path.join(project_path, "screenshots")

# ========== 第一步：初始化logger（必须在创建目录前） ==========
def setup_logger():
    log_filename = os.path.join(LOG_DIR, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# ========== 第二步：创建目录（此时logger已定义） ==========
for dir_path in [LOG_DIR, SCREENSHOTS_DIR]:
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"创建目录成功：{dir_path}")
    except Exception as e:
        logger.error(f"创建目录失败：{dir_path}，错误原因：{str(e)}")

# ========== 后续的Driver夹具、截图夹具、钩子逻辑完全不变 ==========
# ... 以下保留之前修正后的driver夹具、截图夹具、pytest钩子 ...
