import unittest
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class AddToCartPage(BasePage):
    #商品卡片
    products_01 = (By.XPATH, '//div[@class="goods-item"]/a[@target="_blank" and contains(@href, "product_id=")]')
    #商品详情页
    product_title = (By.XPATH, '//h2[contains(text(),"Xiaomi 17 Ultra")]')

    # 手机版本以及选择后
    product_version = (By.XPATH, '//li[@title="16GB+512GB"]')
    product_version_select =(By.XPATH, '//li[@title="16GB+512GB" and contains(@class,"active")]')

    # 手机颜色以及选择后
    product_color = (By.CSS_SELECTOR, 'li[title="白色"]')
    product_color_select = (By.CSS_SELECTOR, 'li[title="白色"].active')


    # 手机附加服务勾选
    product_service = (By.CSS_SELECTOR, 'i[class="iconfont icon-checkbox"]')
    # 点击加入购物车按钮
    product_add_cart = (By.XPATH, '//a[contains(@class, "btn-primary") and text()="加入购物车"]')
    #购物车数量
    cart_count = (By.XPATH,'//span[contains(@class,"cart-mini-num") and contains(@class,"J_cartNum")]')
    #购物车页面
    cart_title= (By.XPATH,'//div[contains(@class,"header-title") and contains(@class,"has-more")]/h2[contains(text(),"我的购物车")]')
    product_delete_btn = (By.XPATH,'//div[contains(@class,"col-action")]/a[contains(@title,"删除")]')
    del_confirm_btn = (By.XPATH,'//button[contains(@class,"btn-primary") and contains(text(),"确定")]')
    del_confirm_title = (By.CLASS_NAME,"del-confirm-title")
    # 加入购物车成功
    add_cart_successed = (By.XPATH, '//div[@class="goods-info"]/h3[contains(text(),"已成功加入购物车！")]')


    def add_to_cart(self):
        #新开一个标签页时，先记录原标签页的句柄
        original_handle = self.driver.current_window_handle
        self.elem_click(self.products_01)
        #等待第二个标签页打开
        WebDriverWait(self.driver,10).until(EC.number_of_windows_to_be(2))
        #找到所有页面的句柄
        all_handles = self.driver.window_handles
        #找到不是预原句柄的标签页
        for handle in all_handles:
            if handle != original_handle:
                self.driver.switch_to.window(handle)
                break
        self.wait_elem_visible(self.product_title)
        self.elem_click(self.product_color)
        self.wait_elem_visible(self.product_color_select)

        self.elem_click(self.product_version)
        self.wait_elem_visible(self.product_version_select)

        self.elem_click(self.product_service)
        self.elem_click(self.product_add_cart)
        add_cart_success_elem = self.wait_elem_visible(self.add_cart_successed)
        return add_cart_success_elem

    def get_cart_count(self):
        try:
            current_cart_elem = self.wait_elem_visible(self.cart_count)
            current_cart_text = current_cart_elem.text.strip()
            # 清洗文本，只保留数字
            cart_num_str = "".join([c for c in current_cart_text if c.isdigit()])
            return int(cart_num_str) if cart_num_str else 0  # 无数字返回0
        except TimeoutException:
            # 元素定位失败时返回0，保证方法不抛异常
            return 0

    def delete_cart(self):
        cart_num = self.get_cart_count()
        if cart_num <= 0:
            self.add_to_cart()
        else:
            self.elem_click(self.cart_count)
            self.wait_elem_visible(self.cart_title)
            self.elem_click(self.product_delete_btn)
            self.wait_elem_visible(self.del_confirm_title)
            self.elem_click(self.del_confirm_btn)
            return cart_num


