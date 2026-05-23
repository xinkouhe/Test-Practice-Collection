#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.log_helper import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.step_timeout = 15
        self.error_timeout = 5

        # 保持与旧脚本一致，优先验证最短路径。
        self.LOGIN_LINK = (By.CSS_SELECTOR, ".m-tophead.f-pr.j-tflag a")
        self.OTHER_LINK = (By.XPATH, '//a[contains(text(), "选择其他登录模式")]')
        self.AGREEMENT_LINK = (By.XPATH, '//*[@id="j-official-terms"]')
        self.PHONE_LINK = (By.XPATH, '//div[contains(text(), "手机号登录/注册")]')
        self.PASSWORD_LINK = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/div[1]/a")

        self.PHONE_INPUT = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[1]/div/input")
        self.PASSWORD_INPUT = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[2]/div/input")
        self.LOGIN_BUTTON = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/section/a/div")

        self.ERROR_MESSAGE_LOCATORS = [
            (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[3]/span"),
            (By.XPATH, "//section/div[3]/span"),
            (
                By.XPATH,
                '//span[contains(normalize-space(.), "请输入") or contains(normalize-space(.), "账号或密码错误")]',
            ),
        ]

    def log_step(self, message):
        logger.info(message)
        print(message)

    def click_step(self, step_no, step_name, locator):
        self.click(locator, timeout=self.step_timeout)
        self.log_step(f"【{step_no}】success {step_name}")

    def input_step(self, step_no, step_name, locator, text):
        self.input_text(locator, text, timeout=self.step_timeout)
        self.log_step(f"【{step_no}】success {step_name}")

    def get_error_message(self):
        last_error = None
        for locator in self.ERROR_MESSAGE_LOCATORS:
            try:
                text = self.get_text(locator, timeout=self.error_timeout)
                logger.info("命中错误提示定位器: %s -> %s", locator, text)
                return text
            except Exception as exc:
                last_error = exc
                logger.exception("读取错误提示失败，尝试下一个定位器: %s", locator)

        if last_error is not None:
            raise last_error
        raise RuntimeError("未读取到错误提示文本")

    def login(self, phone, password):
        try:
            self.click_step("1", "click_login_link", self.LOGIN_LINK)
            self.click_step("2", "click_other_link", self.OTHER_LINK)
            self.click_step("3", "click_agreement_link", self.AGREEMENT_LINK)
            self.click_step("4", "click_phone_link", self.PHONE_LINK)
            self.click_step("5", "click_password_link", self.PASSWORD_LINK)
            self.input_step("6", "input_phone", self.PHONE_INPUT, phone)
            self.input_step("7", "input_password", self.PASSWORD_INPUT, password)
            self.click_step("8", "click_login_button", self.LOGIN_BUTTON)
        except Exception as exc:
            logger.exception("登录流程执行失败")
            self.log_step(f"【ERROR】登录流程执行失败: {exc}")
            raise
