from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BuyPage(BasePage):
    #[去购物车结算]按钮
    to_checkout_btn = (By.XPATH, '//a[@class="cart-mini" and contains(text(), "购物车")]')
    #产品确认页面
    product_name = (By.XPATH,'//h3[@class="name"]/a[contains(text(),"Xiaomi 17 Ultra")]')
    #结算按钮
    checkout_btn = (By.CSS_SELECTOR, ".btn.btn-a.btn-primary")
    confirm_order = (By.XPATH,'//div[@id="J_miniHeaderTitle"]/h2[contains(normalize-space(text()), "确认订单")]')
    #选择地址
    address = (By.XPATH, '//div[@class="address-info" and .//div[@class="tel" and contains(text(),"176****9450")]]')
    #点击付款
    order_btn = (By.XPATH, '//div[@class="operating-button"]/a[contains(text(),"立即下单")]')
    #下单成功
    order_success = (By.XPATH,'//div[@class="fl"]/h2[@class="title" and contains(text(),"订单提交成功！去付款咯～")]')

    def buy(self):
        self.elem_click(self.to_checkout_btn)
        self.wait_elem_visible(self.product_name)
        self.elem_click(self.checkout_btn)
        self.wait_elem_visible(self.confirm_order)
        self.elem_click(self.address)
        self.elem_click(self.order_btn)
        order_success_elem = self.wait_elem_visible(self.order_success)
        return order_success_elem












