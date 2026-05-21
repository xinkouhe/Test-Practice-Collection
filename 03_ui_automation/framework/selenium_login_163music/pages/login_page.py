#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.log_helper import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # 这里直接保持与旧脚本一致，先恢复一条可验证的稳定链路。
        self.LOGIN_LINK = (By.CSS_SELECTOR, ".m-tophead.f-pr.j-tflag a")
        self.OTHER_LINK = (By.XPATH, '//a[contains(text(), "选择其他登录模式")]')
        self.AGREEMENT_LINK = (By.XPATH, '//*[@id="j-official-terms"]')
        self.PHONE_LINK = (By.XPATH, '//div[contains(text(), "手机号登录/注册")]')
        self.PASSWORD_LINK = (By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/div[1]/a')

        self.PHONE_INPUT = (By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[1]/div/input')
        self.PASSWORD_INPUT = (By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[2]/div/input')
        self.LOGIN_BUTTON = (By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/section/a/div')

        self.ERROR_MESSAGE_LOCATORS = [
            (By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[3]/span'),
            (By.XPATH, '//section/div[3]/span'),
            (
                By.XPATH,
                '//span[contains(normalize-space(.), "请输入") or contains(normalize-space(.), "账号或密码错误")]',
            ),
        ]

    def log_step(self, message):
        logger.info(message)
        print(message)

    def pause(self, seconds):
        logger.info("等待页面稳定: %s 秒", seconds)
        time.sleep(seconds)

    def find_raw_element(self, locator):
        logger.info("直接定位元素: %s", locator)
        return self.driver.find_element(*locator)

    def js_click_raw(self, locator):
        element = self.find_raw_element(locator)
        self.driver.execute_script("arguments[0].click();", element)

    def safe_click_raw(self, locator, timeout=10):
        # 先走普通点击，只有在普通点击不稳时才退回 JS 点击。
        element = self.find_element(locator, timeout=timeout)
        try:
            element.click()
            return
        except Exception:
            logger.exception("普通点击失败，准备尝试滚动后再次点击: %s", locator)

        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                element,
            )
            self.pause(1)
            element.click()
            return
        except Exception:
            logger.exception("滚动后普通点击仍失败，退回 JS 点击: %s", locator)

        self.driver.execute_script("arguments[0].click();", element)

    def input_raw(self, locator, text):
        element = self.find_raw_element(locator)
        element.clear()
        if text is not None:
            element.send_keys(text)

    def click_login_link(self):
        self.safe_click_raw(self.LOGIN_LINK)

    def click_other_link(self):
        self.safe_click_raw(self.OTHER_LINK)

    def click_agreement_link(self):
        self.js_click_raw(self.AGREEMENT_LINK)

    def click_phone_link(self):
        self.js_click_raw(self.PHONE_LINK)

    def click_password_link(self):
        self.js_click_raw(self.PASSWORD_LINK)

    def input_phone(self, phone):
        self.input_raw(self.PHONE_INPUT, phone)

    def input_password(self, password):
        self.input_raw(self.PASSWORD_INPUT, password)

    def click_login_button(self):
        element = self.find_raw_element(self.LOGIN_BUTTON)
        element.click()

    def get_error_message(self):
        last_error = None
        for locator in self.ERROR_MESSAGE_LOCATORS:
            try:
                text = self.get_text(locator)
                logger.info("命中错误提示定位器: %s -> %s", locator, text)
                return text
            except Exception as exc:
                last_error = exc
                logger.exception("读取错误提示失败，尝试下一个定位器: %s", locator)

        if last_error is not None:
            raise last_error
        raise RuntimeError("未读取到错误提示文案")

    def login(self, phone, password):
        try:
            self.click_login_link()
            self.log_step("【1】success click_login_link")
            self.pause(2)

            self.click_other_link()
            self.log_step("【2】success click_other_link")
            self.pause(2)

            self.click_agreement_link()
            self.log_step("【3】success click_agreement_link")
            self.pause(1)

            self.click_phone_link()
            self.log_step("【4】success click_phone_link")
            self.pause(3)

            self.click_password_link()
            self.log_step("【5】success click_password_link")
            self.pause(2)

            self.input_phone(phone)
            self.log_step("【6】success input_phone")
            self.pause(1)

            self.input_password(password)
            self.log_step("【7】success input_password")
            self.pause(1)

            self.click_login_button()
            self.log_step("【8】success click_login_button")

        except Exception as e:
            logger.exception("登录流程执行失败")
            self.log_step(f"【ERROR】卡在上面某一步，具体错误: {e}")
            raise
