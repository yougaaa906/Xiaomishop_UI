import os
import sys
import pytest
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ========== 1. 基础路径配置（兼容本地+流水线） ==========
# 获取项目根目录
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# 导入配置文件（确保config/config.py已提交到GitHub）
from config.config import TIMEOUT, TEST_URL, CHROME_DRIVER_PATH

# 定义日志/截图路径
LOG_DIR = os.path.join(project_path, "logs")
SCREENSHOTS_DIR = os.path.join(project_path, "screenshots")

# ========== 2. 日志配置（核心修复：先创建日志目录） ==========
def setup_logger():
    # 优先创建日志目录，避免日志文件创建失败
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
    
    # 生成带时间戳的日志文件名
    log_filename = os.path.join(LOG_DIR, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # 配置日志（终端+文件双输出，中文不乱码）
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

# 初始化logger（全局可用）
logger = setup_logger()

# ========== 3. 创建截图目录（单独处理，避免影响日志） ==========
try:
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        logger.info(f"✅ 截图目录创建成功：{SCREENSHOTS_DIR}")
except Exception as e:
    logger.error(f"❌ 截图目录创建失败：{SCREENSHOTS_DIR}，错误：{str(e)}")

# ========== 4. 核心Driver夹具（兼容本地/流水线，异常捕获） ==========
@pytest.fixture(scope="function")
def driver():
    driver = None
    try:
        # Chrome选项配置
        chrome_options = Options()
        
        # 优化：禁用图片加载，提升执行速度
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 判断是否为GitHub流水线环境（CI=true）
        is_ci = os.getenv("CI", "false") == "true"
        
        if is_ci:
            # 流水线配置：无头模式+Ubuntu适配（兼容所有Chrome版本）
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            logger.info("🔧 检测到CI环境，启用无头模式运行Chrome")
        else:
            # 本地配置：有界面最大化
            chrome_options.add_argument("--start-maximized")
            logger.info("🔧 本地环境，启用有界面最大化运行Chrome")
        
        # 自动下载匹配版本的ChromeDriver（无需手动维护）
        chrome_service = Service(ChromeDriverManager().install())
        logger.info(f"✅ ChromeDriver下载成功，路径：{chrome_service.path}")
        
        # 初始化浏览器
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.implicitly_wait(TIMEOUT)
        driver.set_page_load_timeout(TIMEOUT)
        logger.info(f"✅ 浏览器初始化成功，测试基础URL：{TEST_URL}")
        
        yield driver

    except Exception as e:
        # 捕获所有初始化异常，详细记录便于排查
        logger.error(f"❌ 浏览器初始化失败：{str(e)}", exc_info=True)
        raise  # 抛出异常，让用例失败，不静默

    finally:
        # 无论是否成功，都关闭浏览器（避免进程残留）
        if driver:
            try:
                driver.quit()
                logger.info("✅ 浏览器已正常关闭")
            except Exception as e:
                logger.error(f"❌ 浏览器关闭失败：{str(e)}")

# ========== 5. 失败自动截图（自动生效，兼容流水线） ==========
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    yield  # 执行用例

    # 兼容处理：避免未获取到用例结果时报错
    try:
        if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
            # 处理用例名特殊字符，避免路径报错
            case_name = request.node.name
            case_name_safe = case_name.replace("/", "_").replace("\\", "_").replace(":", "_")
            
            # 生成截图文件名（用例名+时间戳）
            screenshot_name = f"{case_name_safe}_fail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)

            # 保存截图并记录日志
            try:
                driver.save_screenshot(screenshot_path)
                logger.error(f"❌ 用例【{case_name}】执行失败，截图已保存：{screenshot_path}")
            except Exception as e:
                logger.error(f"❌ 用例【{case_name}】截图保存失败：{str(e)}")
    except Exception as e:
        logger.error(f"❌ 失败截图逻辑执行出错：{str(e)}")

# ========== 6. pytest钩子（获取用例执行结果） ==========
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """获取用例执行结果，给失败截图提供判断依据"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
    logger.info(f"📝 用例【{item.name}】{rep.when}阶段结果：{rep.outcome}")
