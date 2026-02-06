from config.config import USERNAME,PASSWORD
from pages.loginpage import LoginPage
import logging
from pages.base_page import BasePage

logger = logging.getLogger(__name__)



def login_common(driver,username=USERNAME, password=PASSWORD):
    login_page = LoginPage(driver)

    login_page.elem_click(login_page.login_entry)
    login_page.elem_click(login_page.agree_protocol_btn)
    login_page.wait_elem_visible(login_page.login_modal)
    login_page.elem_input(login_page.account_input, username)
    login_page.elem_input(login_page.pwd_input, password)
    login_page.elem_click(login_page.checkbox)
    login_page.elem_click(login_page.login_btn)
    username_login = login_page.wait_elem_visible(login_page.username_elem)

    logger.info("通⽤登录步骤完成")



