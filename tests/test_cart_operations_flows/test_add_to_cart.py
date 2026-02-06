import pytest
from pages.loginpage import LoginPage
from pages.searchpage import SearchPage
from pages.add_to_cart_page import AddToCartPage
from pages.buypage import BuyPage
from config.config import USERNAME, PASSWORD, KEYWORD
import logging
from tests.common import login_common


logger = logging.getLogger(__name__)

# 流程第1步：登录（order=1，最先执行）
@pytest.mark.cart
def test_add_to_cart_flow(driver):
    logger.info("\n=======完整加购流程======")

    try:
        #登录
        login_common(driver)
        logger.info("登陆步骤完成")


        #搜索
        search_page = SearchPage(driver)
        search_result = search_page.search(KEYWORD)
        assert search_result>1,f"搜索{KEYWORD}无结果"
        logger.info("搜索有结果返回")

        #加购物车


        add_to_cart_page = AddToCartPage(driver)
        add_to_cart_result = add_to_cart_page.add_to_cart()
        assert "已成功加入购物车" in add_to_cart_result.text.strip(), "加入购物车失败"
        logger.info("加入购物车成功")


    except Exception as e:
        logger.error(f"完整加购流程失败：{str(e)},exc_info=True")
        raise e