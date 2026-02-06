import pytest
from pages.loginpage import LoginPage
from pages.searchpage import SearchPage
from pages.add_to_cart_page import AddToCartPage
from pages.buypage import BuyPage
from config.config import WRONG_USERNAME, PASSWORD, KEYWORD
import logging
from tests.common import login_common


logger = logging.getLogger(__name__)

# 流程第1步：登录（order=1，最先执行）
@pytest.mark.abnormal
def test_login_fail_flow(driver):
    logger.info("\n=======登录失败流程======")

    try:
        #登录
        login_page = LoginPage(driver)
        login_fail_elem = login_page.login_fail(username=WRONG_USERNAME, password=PASSWORD)
        assert "用户名或密码不正确" in login_fail_elem,"登录失败测试不通过"
        logger.info("登陆失败步骤完成")



    except Exception as e:
        logger.error(f"登录失败流程不通过：{str(e)},exc_info=True")
        raise e