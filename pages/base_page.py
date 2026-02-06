from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from config.config import TIMEOUT
import os

#封装测试脚本中用的比较多的操作，把这些操作写成方法，脚本中就只需要调用函数即可
class BasePage:
    def __init__(self,driver):
        self.driver = driver
    #封装通用的等待方法
    def wait_elem_visible(self,locator,timeout=None):
        #若未传时间，则采用配置文件中的时间默认值
        timeout = TIMEOUT or timeout
        try:
            elem = WebDriverWait(self.driver,timeout).until(EC.visibility_of_element_located(locator))
            return elem
        except TimeoutException:
            self.driver.save_screenshot(f"elem_timeout_{locator[1]}.png")
            raise TimeoutException(f"元素定位超时:{locator}")

    #封装通用的元素可点击方法
    def elem_clickable(self,locator,timeout=None):
        timeout = timeout or TIMEOUT
        try:
            elem = WebDriverWait(self.driver,timeout).until(EC.element_to_be_clickable(locator))
            return elem
        except TimeoutException:
            self.driver.save_screenshot(f"elem_timeout：{locator[1]}.png")
            raise TimeoutException(f"元素可点击超时：{locator}")
    #封装通用的点击方法
    def elem_click(self,locator,timeout=None):
        timeout = timeout or TIMEOUT
        elem = self.elem_clickable(locator,timeout)
        elem.click()

    #封装通用的输入方法

    def elem_input(self,locator,text,timeout=None):
        timeout = timeout or TIMEOUT
        elem = self.wait_elem_visible(locator,timeout)
        elem.clear()
        elem.send_keys(text)

    #封装截图保存方法
    def save_screen_shot(self,filename):
        #确保截图路径存在，如果不存在，则创建
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        screenshots_path = os.path.join("screenshots",filename)
        self.driver.save_screenshot(screenshots_path)
        return screenshots_path

    #封装标签页跳转方法
    def open_new_tab(self,locator):
        original_handles = self.driver.window_handles
        original_count = len(original_handles)
        self.elem_click(locator)
        #必须要等待新的标签页先创建
        WebDriverWait(self.driver,15).until(lambda x:len(x.window_handles)>original_count)

        all_windows = self.driver.window_handles
        new_window = None
        for win in all_windows:
            if win not in original_handles:
                new_window = win
                self.driver.switch_to.window(new_window)
                break




