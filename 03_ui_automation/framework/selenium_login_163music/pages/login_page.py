#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # 定位器，CSS数量较少，无需专门的locators封装
        self.LOGIN_LINK = (By.CSS_SELECTOR, "a.link[data-action='login']")
        self.OTHER_LINK = (By.CSS_SELECTOR, "a[data-log*='btn_web_other_login_method']")
        self.AGREEMENT_LINK = (By.CSS_SELECTOR, "input[type='checkbox'][data-log*='cell_web_agreement_check_box']")
        self.PHONE_LINK = (By.CSS_SELECTOR, "a[data-log*='btn_web_mobile_number_login'] > div.tan2MIhq")
        self.PASSWORD_LINK = (By.CSS_SELECTOR, "div[data-log*='page_web_register_login'] > a[href='javascript:;']:first-of-type")

        self.PHONE_INPUT = (By.CSS_SELECTOR, "input[type='text'][placeholder='请输入手机号']")
        self.PASSWORD_INPUT = (By.CSS_SELECTOR, ".mrc-modal-container input[type='password']")
        self.LOGIN_BUTTON = (By.CSS_SELECTOR, "div[data-log*=page_web_register_login] > .tan2MIhq")

        self.ERROR_MESSAGE = (By.CSS_SELECTOR, "div[data-log*=page_web_register_login] > span")

    def click_login_link(self):
        self.click(self.LOGIN_LINK)

    def click_other_link(self):
        self.click(self.OTHER_LINK)

    def click_agreement_link(self):
        self.click(self.AGREEMENT_LINK)

    def click_phone_link(self):
        self.click(self.PHONE_LINK)

    def click_password_link(self):
        self.click(self.PASSWORD_LINK)

    def input_phone(self, phone):
        self.input_text(locator=self.PHONE_INPUT, text=phone)

    def input_password(self, password):
        self.input_text(locator=self.PASSWORD_INPUT, text=password)

    def click_login_button(self):
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)

    def login(self, phone, password):
        self.click_login_link()
        self.click_other_link()
        self.click_agreement_link()
        self.click_phone_link()
        self.click_password_link()
        self.input_phone(phone)
        self.input_password(password)
        self.click_login_button()