import pytest
import logging
from pages.add_to_cart_page import AddToCartPage
from config.config import KEYWORD
from tests.common import login_common
from pages.searchpage import SearchPage

logger = logging.getLogger(__name__)


@pytest.mark.cart
def test_delete_cart(driver):
    logger.info("\n======删除购物车中的产品用例开始执行=======")
    try:
        # 1. 前置登录
        login_common(driver)
        logger.info("登录成功")

        # 2. 搜索商品
        search_page = SearchPage(driver)
        search_result = search_page.search(KEYWORD)
        assert search_result > 1, f"搜索{KEYWORD}无结果，无法继续操作"
        logger.info(f"搜索{KEYWORD}有结果返回，共{search_result}个商品")

        # 3. 初始化加购/删除页面
        cart_page = AddToCartPage(driver)

        # 4. 显式判断购物车是否有商品（核心补充）
        cart_num = cart_page.get_cart_count()
        if cart_num == 0:
            logger.info("购物车无商品，先执行加购操作")
            # 执行加购
            cart_page.add_to_cart()
            # 加购后重新获取数量
            cart_num = cart_page.get_cart_count()
            logger.info(f"加购成功，当前购物车数量：{cart_num}")
        else:
            logger.info(f"购物车已有商品，数量：{cart_num}")

        # 5. 执行删除操作
        cart_page.elem_click(cart_page.cart_count)  # 进入购物车页面
        cart_page.wait_elem_visible(cart_page.cart_title)  # 等待购物车页面加载
        cart_page.elem_click(cart_page.product_delete_btn)  # 点击删除按钮
        cart_page.wait_elem_visible(cart_page.del_confirm_title)  # 等待删除确认弹窗
        cart_page.elem_click(cart_page.del_confirm_btn)  # 确认删除

        # 6. 断言删除成功（数量为0）
        del_after_num = cart_page.get_cart_count()
        assert del_after_num == 0, f"删除失败！删除前数量：{cart_num}，删除后数量：{del_after_num}"
        logger.info("购物车商品删除成功，用例执行通过")

    except Exception as e:
        logger.error(f"购物车删除流程失败：{str(e)}", exc_info=True)
        raise e