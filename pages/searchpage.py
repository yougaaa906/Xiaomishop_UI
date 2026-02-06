import unittest
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException



class SearchPage(BasePage):
    #搜索框输入
    search_field = (By.ID,"search")
    #点击搜索按钮
    search_btn = (By.CSS_SELECTOR,'input[class="search-btn iconfont"]')
    #搜索结果数量
    product_items = (By.CSS_SELECTOR,'div[class="goods-item"]')

    def search(self,keyword="手机"):
        self.elem_input(self.search_field,keyword)
        self.elem_click(self.search_btn)
        self.wait_elem_visible(self.product_items)
        product_elems = self.driver.find_elements(*self.product_items)

        product_count = len(product_elems)
        return product_count









