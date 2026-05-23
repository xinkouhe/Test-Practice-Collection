#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础页面方法。
统一使用同一种显式等待，避免混用可见性、可点击等多种判断。
"""

from selenium.webdriver.support.wait import WebDriverWait

from utils.log_helper import get_logger
from utils.log_helper import save_driver_screenshot

logger = get_logger(__name__)


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 15

    def _build_wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout, poll_frequency=0.5)

    def wait_for_element(self, locator, timeout=None):
        def _locate(driver):
            elements = driver.find_elements(*locator)
            return elements[0] if elements else False

        return self._build_wait(timeout).until(_locate)

    def wait_for_text(self, locator, timeout=None):
        def _locate(driver):
            elements = driver.find_elements(*locator)
            if not elements:
                return False

            text = elements[0].text.strip()
            return text or False

        return self._build_wait(timeout).until(_locate)

    def click(self, locator, timeout=None):
        logger.info("使用 JS 点击元素: %s", locator)
        element = self.wait_for_element(locator, timeout=timeout)
        self.driver.execute_script("arguments[0].click();", element)

    def input_text(self, locator, text, timeout=None):
        logger.info("输入元素已定位: %s", locator)
        element = self.wait_for_element(locator, timeout=timeout)
        element.clear()
        if text is not None:
            element.send_keys(text)

    def get_text(self, locator, timeout=None):
        return self.wait_for_text(locator, timeout=timeout)

    def take_screenshot(self, name="page"):
        screenshot_path = save_driver_screenshot(self.driver, name)
        if screenshot_path is not None:
            logger.info("截图已保存: %s", screenshot_path.resolve())
        return screenshot_path
