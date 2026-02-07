import os
import sys
import urllib3
urllib3.Timeout.DEFAULT_TIMEOUT = urllib3.Timeout(total=10)




'''
完善点	    作用	对你的价值
1. 日志配置,作用：把执行过程（初始化浏览器、用例失败、截图）记录到日志文件 + 终端，目的：出问题时不用猜，看日志就能定位 “是驱动错了？还是页面没打开？”
2. 失败自动截图，作用：用例失败时自动保存截图到screenshots文件夹	目的：可视化排查失败原因（比如 “元素没找到” 是因为页面加载错了）
3. 异常捕获（浏览器初始化），作用：初始化失败时记录详细错误，避免 “静默失败”，目的：驱动路径错、浏览器版本不匹配时，能直接看到错误原因
4. 自动创建文件夹，作用：日志 / 截图文件夹不存在时自动创建，目的：不用手动建文件夹，避免 “保存截图 / 日志时路径不存在” 报错
5. finally 关闭浏览器	作用：无论初始化是否成功，都尝试关闭浏览器	目的：避免 “浏览器进程残留”（比如初始化失败后，Chrome 进程还在后台）
6. 禁用图片加载（可选）	作用：减少页面加载资源，提升用例执行速度	目的：自动化不用看图片，执行更快，尤其网络差时更明显
'''
#日志、截图路径配置
#获取项目根目录,__file__ 是当前脚本的路径，os.path.abspath() 把它转成绝对路径，os.path.dirname() 提取路径的目录部分。
project_path = os.path.dirname(os.path.abspath(__file__))
#把项目路径根目录放进python的搜索路径
sys.path.append(project_path)

import pytest
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from config.config import TIMEOUT, TEST_URL, CHROME_DRIVER_PATH

#定义日志、截图的路径
LOG_DIR = os.path.join(project_path,"logs")
SCREENSHOTS_DIR = os.path.join(project_path,"screenshots")
#检索日志、截图的路径，没有则创建
for dir_path in [LOG_DIR,SCREENSHOTS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

#日志配置
def setup_logger():
    log_filename = os.path.join(LOG_DIR, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s",handlers=[logging.FileHandler(log_filename, encoding="utf-8"),logging.StreamHandler()])
    return logging.getLogger(__name__)

logger = setup_logger()


@pytest.fixture(scope="function")
def driver():
    # 初始化Chrome选项
    chrome_options = Options()
    
    # 关键：判断是否是GitHub流水线环境（通过环境变量）
    # GitHub Actions会自动设置CI=true的环境变量
    is_ci = os.getenv("CI", "false") == "true"
    
    if is_ci:
        # 流水线环境：开启无头模式+适配Ubuntu
        chrome_options.add_argument("--headless")  # 无界面
        chrome_options.add_argument("--no-sandbox")  # Ubuntu权限
        chrome_options.add_argument("--disable-dev-shm-usage")  # 资源限制
    else:
        # 本地环境：有界面运行（方便调试），可加窗口大小
        chrome_options.add_argument("--start-maximized")  # 窗口最大化
    
    # 自动下载匹配版本的ChromeDriver（核心）
    chrome_service = Service(ChromeDriverManager().install())
    
    # 初始化driver
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.implicitly_wait(10)  # 隐式等待
    yield driver
    
    # 清理资源
    driver.quit()


# ========== 3. 失败自动截图夹具（新增，自动生效） ==========
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    """
    用例失败自动截图：
    - scope="function"：每个用例执行后检查
    - autouse=True：自动生效，无需手动调用
    """
    yield  # 执行用例

    # 检查用例是否失败
    if request.node.rep_call.failed:
        # 生成截图文件名（用例名+时间戳，避免重复）
        case_name = request.node.name
        screenshot_name = f"{case_name}_fail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)

        # 保存截图并记录日志
        try:
            driver.save_screenshot(screenshot_path)
            logger.error(f"用例【{case_name}】执行失败，截图已保存至：{screenshot_path}")
        except Exception as e:
            logger.error(f"用例【{case_name}】失败截图保存失败！错误原因：{str(e)}")


# ========== 4. 修复pytest用例结果获取（新增，必须加） ==========
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """获取用例执行结果，给fail_screenshot提供判断依据"""
    outcome = yield
    rep = outcome.get_result()
    # 给用例对象添加结果属性（rep_call：执行阶段结果）
    setattr(item, f"rep_{rep.when}", rep)









