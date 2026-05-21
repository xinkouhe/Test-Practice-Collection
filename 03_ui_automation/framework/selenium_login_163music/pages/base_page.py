#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基类，封装定位元素、点击、输入内容、获取文本；
待补充截图、打开页面
"""

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.log_helper import get_logger
from utils.log_helper import save_driver_screenshot

logger = get_logger(__name__)

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 20
        self.wait = WebDriverWait(self.driver, self.timeout)

    def _build_wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout)

    def find_element(self, locator, timeout=None):
        return self._build_wait(timeout).until(EC.visibility_of_element_located(locator))

    def find_present_element(self, locator, timeout=None):
        return self._build_wait(timeout).until(EC.presence_of_element_located(locator))

    def click(self, locator, by_js=False, timeout=None):
        if by_js:
            logger.info("使用 JS 点击元素: %s", locator)
            self.js_click(locator, timeout=timeout)
            return

        logger.info("点击元素: %s", locator)
        element = self._build_wait(timeout).until(EC.element_to_be_clickable(locator))
        try:
            element.click()
        except Exception:
            self.js_click(locator, timeout=timeout, element=element)

    def js_click(self, locator, timeout=None, element=None):
        if element is None:
            element = self.find_present_element(locator, timeout=timeout)

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});"
            "arguments[0].click();",
            element,
        )

    def input_text(self, locator, text):
        logger.info("输入元素已定位: %s", locator)
        element = self.find_element(locator)
        element.clear()
        if text is not None:
            element.send_keys(text)

    def get_text(self, locator):
        element = self.find_element(locator)
        return element.text.strip()

    def take_screenshot(self, name="page"):
        screenshot_path = save_driver_screenshot(self.driver, name)
        if screenshot_path is not None:
            logger.info("截图已保存: %s", screenshot_path.resolve())
        return screenshot_path

    def open_url(self):
        pass


