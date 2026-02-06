import unittest
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import WRONG_USERNAME,PASSWORD



#如果想让登录调用，则抽离登录，只在其中写登录方法，因此单独写一个脚本，此登录脚本作为单独的用例执行，不可被调用
class LoginPage(BasePage):
    #封装登录操作中的所有元素定位
    #登录入口
    login_entry = (By.CSS_SELECTOR, 'a[data-login="true"]')
    #用户协议同意按钮
    agree_protocol_btn = (By.XPATH, '//button[text()="同意"]')
    #登录弹窗
    login_modal = (By.CSS_SELECTOR, 'div[class="mi-layout__card"]')
    #用户名
    account_input = (By.CSS_SELECTOR, 'input[name="account"]')
    #密码
    pwd_input =(By.CSS_SELECTOR, 'input[name="password"]')
    #个人同意勾选
    checkbox = (By.CSS_SELECTOR, 'span[class="ant-checkbox"]')
    #登录按钮
    login_btn = (By.XPATH, '//button[text()="登录"]')
    #登陆后的用户名
    username_elem = (By.CSS_SELECTOR, 'span.name')
    #登录失败提醒
    error_login_tip = (By.ID,"mi-form-error-form")

    #封装登录操作
    def login(self,username="17695449450",password="zhangruijie906"):
        self.elem_click(self.login_entry)
        self.elem_click(self.agree_protocol_btn)
        self.wait_elem_visible(self.login_modal)
        self.elem_input(self.account_input,username)
        self.elem_input(self.pwd_input,password)
        self.elem_click(self.checkbox)
        self.elem_click(self.login_btn)
        username_login = self.wait_elem_visible(self.username_elem)
        return username_login.text.strip()

    def login_fail(self,username=WRONG_USERNAME,password=PASSWORD):
        self.elem_click(self.login_entry)
        self.elem_click(self.agree_protocol_btn)
        self.wait_elem_visible(self.login_modal)
        self.elem_input(self.account_input, username)
        print(username)
        self.elem_input(self.pwd_input, password)
        self.elem_click(self.checkbox)
        self.elem_click(self.login_btn)
        error_login = self.wait_elem_visible(self.error_login_tip)
        return error_login.text.strip()



