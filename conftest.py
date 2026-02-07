import os
import sys
import urllib3
urllib3.Timeout.DEFAULT_TIMEOUT = urllib3.Timeout(total=10)

# ========== 核心修复：解决路径/导入/兼容性问题 ==========
# 获取项目根目录（兼容本地+流水线）
# 注意：__file__是当前conftest.py的路径，需确保它在项目根目录或正确向上取目录
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# 导入核心模块（补全漏导入的ChromeDriverManager）
import pytest
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# 关键：补全ChromeDriverManager的导入（必加）
from webdriver_manager.chrome import ChromeDriverManager

# ========== 配置修复：移除对config.py的依赖（避免缺失报错） ==========
# 直接定义常量，替代config/config.py的导入（如果有config.py，需确保提交到GitHub）
TIMEOUT = 10  # 隐式等待时间
TEST_URL = "https://www.mi.com"  # 测试基础URL（按你的项目改）
# 流水线中不用手动指定驱动路径，注释掉即可
# CHROME_DRIVER_PATH = ""

# ========== 路径配置（兼容本地+流水线） ==========
LOG_DIR = os.path.join(project_path, "logs")
SCREENSHOTS_DIR = os.path.join(project_path, "screenshots")
# 自动创建目录（加异常捕获，避免权限问题）
for dir_path in [LOG_DIR, SCREENSHOTS_DIR]:
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)  # exist_ok=True避免重复创建报错
            logger.info(f"创建目录成功：{dir_path}")
    except Exception as e:
        logger.error(f"创建目录失败：{dir_path}，错误原因：{str(e)}")

# ========== 日志配置（优化编码和格式） ==========
def setup_logger():
    log_filename = os.path.join(LOG_DIR, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    # 优化：加encoding='utf-8'避免中文乱码，加datefmt统一时间格式
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler()  # 终端输出
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# ========== 核心Driver夹具（修复异常捕获+环境适配） ==========
@pytest.fixture(scope="function")
def driver():
    driver = None
    try:
        # 初始化Chrome选项
        chrome_options = Options()
        
     
        
        # 判断是否为GitHub流水线环境
        is_ci = os.getenv("CI", "false") == "true"
        
        if is_ci:
            # 流水线环境配置（无头+Ubuntu适配）
            chrome_options.add_argument("--headless=new")  # 新版无头模式，更稳定
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")  # 禁用GPU，避免无头模式报错
            logger.info("检测到CI环境，启用无头模式运行Chrome")
        else:
            # 本地环境配置
            chrome_options.add_argument("--start-maximized")
            logger.info("本地环境，启用有界面最大化运行Chrome")
        
        # 自动下载匹配版本的ChromeDriver
        chrome_service = Service(ChromeDriverManager().install())
        logger.info(f"ChromeDriver自动下载路径：{chrome_service.path}")
        
        # 初始化driver
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.implicitly_wait(TIMEOUT)
        driver.set_page_load_timeout(TIMEOUT)  # 页面加载超时
        logger.info(f"浏览器初始化成功，基础测试URL：{TEST_URL}")
        
        yield driver

    except Exception as e:
        # 异常捕获：记录详细错误，便于排查
        logger.error(f"浏览器初始化失败！错误原因：{str(e)}", exc_info=True)
        raise  # 抛出异常，让用例失败，不静默
        
    finally:
        # 无论是否成功，都尝试关闭浏览器（避免进程残留）
        if driver:
            try:
                driver.quit()
                logger.info("浏览器已正常关闭")
            except Exception as e:
                logger.error(f"浏览器关闭失败！错误原因：{str(e)}")

# ========== 失败自动截图夹具（优化兼容性） ==========
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    yield  # 执行用例

    # 兼容处理：避免未获取到用例结果时报错
    try:
        # 检查用例是否失败
        if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
            case_name = request.node.name
            # 优化：替换用例名中的特殊字符，避免路径报错
            case_name_safe = case_name.replace("/", "_").replace("\\", "_").replace(":", "_")
            screenshot_name = f"{case_name_safe}_fail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)

            # 保存截图
            try:
                driver.save_screenshot(screenshot_path)
                logger.error(f"用例【{case_name}】执行失败，截图已保存：{screenshot_path}")
                # 流水线中上传截图（可选，需在流水线配置中添加上传步骤）
                logger.info(f"流水线截图路径：{screenshot_path}（可在Artifacts中下载）")
            except Exception as e:
                logger.error(f"用例【{case_name}】截图保存失败！错误原因：{str(e)}")
    except Exception as e:
        logger.error(f"失败截图逻辑执行出错：{str(e)}")

# ========== pytest钩子（修复用例结果获取） ==========
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """获取用例执行结果，兼容所有pytest版本"""
    outcome = yield
    rep = outcome.get_result()
    # 给item添加不同阶段的结果（setup/call/teardown）
    setattr(item, f"rep_{rep.when}", rep)
    # 记录用例执行结果日志
    logger.info(f"用例【{item.name}】{rep.when}阶段结果：{rep.outcome}")
