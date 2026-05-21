#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.log_helper import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # 这里先保持与旧脚本一致，优先保证主流程可复现。
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

    def pause(self, seconds):
        logger.info("等待页面稳定: %s 秒", seconds)
        time.sleep(seconds)

    def find_raw_element(self, locator):
        logger.info("直接定位元素: %s", locator)
        return self.driver.find_element(*locator)

    def debug_page_state(self, tag, save_screenshot=False):
        logger.info("开始记录调试信息: %s", tag)
        try:
            state = self.driver.execute_script(
                """
                return (function () {
                    function summarize(el) {
                        if (!el) {
                            return null;
                        }

                        var rect = el.getBoundingClientRect();
                        var style = window.getComputedStyle(el);
                        var text = (el.innerText || el.textContent || "")
                            .replace(/\\s+/g, " ")
                            .trim()
                            .slice(0, 120);

                        return {
                            tag: el.tagName,
                            id: el.id || "",
                            className: typeof el.className === "string" ? el.className : "",
                            text: text,
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            x: Math.round(rect.x),
                            y: Math.round(rect.y)
                        };
                    }

                    function findByXpath(xpath) {
                        try {
                            return document.evaluate(
                                xpath,
                                document,
                                null,
                                XPathResult.FIRST_ORDERED_NODE_TYPE,
                                null
                            ).singleNodeValue;
                        } catch (error) {
                            return null;
                        }
                    }

                    var bodyText = document.body ? (document.body.innerText || "") : "";
                    var modal = document.querySelector(".mrc-modal-wrapper, .m-layer, .zbar");

                    return {
                        url: window.location.href,
                        title: document.title,
                        readyState: document.readyState,
                        loginLink: summarize(document.querySelector(".m-tophead.f-pr.j-tflag a")),
                        otherLink: summarize(findByXpath('//a[contains(text(), "选择其他登录模式")]')),
                        agreementLink: summarize(findByXpath('//*[@id="j-official-terms"]')),
                        phoneLink: summarize(findByXpath('//div[contains(text(), "手机号登录/注册")]')),
                        passwordLink: summarize(findByXpath('/html/body/div[7]/div/div[2]/div/div/div[2]/div[1]/a')),
                        errorTip: summarize(findByXpath('/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[3]/span')),
                        modalPreview: summarize(modal),
                        bodyHints: {
                            hasOtherLoginText: bodyText.includes("选择其他登录模式"),
                            hasPhoneRegisterText: bodyText.includes("手机号登录/注册"),
                            hasPasswordLoginText: bodyText.includes("密码登录"),
                            hasAgreementText: bodyText.includes("同意"),
                            hasPhoneRequiredText: bodyText.includes("请输入手机号"),
                            hasPasswordRequiredText: bodyText.includes("请输入登录密码"),
                            hasAccountErrorText: bodyText.includes("账号或密码错误"),
                            hasSliderText: bodyText.includes("请完成安全验证") || bodyText.includes("向右拖动滑块填充拼图")
                        }
                    };
                })();
                """
            )
            logger.info("页面调试信息[%s]: %s", tag, json.dumps(state, ensure_ascii=False))
        except Exception:
            logger.exception("记录页面调试信息失败: %s", tag)

        if not save_screenshot:
            return

        try:
            screenshot_path = self.take_screenshot(f"debug_{tag}")
            if screenshot_path is not None:
                logger.info("调试截图[%s]: %s", tag, screenshot_path.resolve())
        except Exception:
            logger.exception("保存调试截图失败: %s", tag)

    def js_click_raw(self, locator, step_name=""):
        try:
            element = self.find_raw_element(locator)
            self.driver.execute_script("arguments[0].click();", element)
        except Exception:
            if step_name:
                self.debug_page_state(f"{step_name}_js_click_failed", save_screenshot=True)
            raise

    def safe_click_raw(self, locator, timeout=10, step_name=""):
        if step_name:
            logger.info("准备点击步骤: %s, locator=%s", step_name, locator)

        try:
            element = self.find_element(locator, timeout=timeout)
        except Exception:
            if step_name:
                self.debug_page_state(f"{step_name}_find_failed", save_screenshot=True)
            raise

        try:
            element.click()
            return
        except Exception:
            logger.exception("普通点击失败，准备尝试滚动后再次点击: %s", locator)
            if step_name:
                self.debug_page_state(f"{step_name}_normal_click_failed")

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
            if step_name:
                self.debug_page_state(f"{step_name}_scroll_click_failed", save_screenshot=True)

        self.driver.execute_script("arguments[0].click();", element)

    def input_raw(self, locator, text):
        element = self.find_raw_element(locator)
        element.clear()
        if text is not None:
            element.send_keys(text)

    def click_login_link(self):
        self.safe_click_raw(self.LOGIN_LINK, step_name="click_login_link")

    def click_other_link(self):
        self.safe_click_raw(self.OTHER_LINK, step_name="click_other_link")

    def click_agreement_link(self):
        self.js_click_raw(self.AGREEMENT_LINK, step_name="click_agreement_link")

    def click_phone_link(self):
        self.js_click_raw(self.PHONE_LINK, step_name="click_phone_link")

    def click_password_link(self):
        self.js_click_raw(self.PASSWORD_LINK, step_name="click_password_link")

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
        raise RuntimeError("未读取到错误提示文本")

    def login(self, phone, password):
        current_step = "start"
        try:
            current_step = "click_login_link"
            self.click_login_link()
            self.log_step("【1】success click_login_link")
            self.pause(2)
            self.debug_page_state("after_click_login_link")

            current_step = "click_other_link"
            self.click_other_link()
            self.log_step("【2】success click_other_link")
            self.pause(2)
            self.debug_page_state("after_click_other_link")

            current_step = "click_agreement_link"
            self.click_agreement_link()
            self.log_step("【3】success click_agreement_link")
            self.pause(1)

            current_step = "click_phone_link"
            self.click_phone_link()
            self.log_step("【4】success click_phone_link")
            self.pause(3)
            self.debug_page_state("after_click_phone_link")

            current_step = "click_password_link"
            self.click_password_link()
            self.log_step("【5】success click_password_link")
            self.pause(2)
            self.debug_page_state("after_click_password_link")

            current_step = "input_phone"
            self.input_phone(phone)
            self.log_step("【6】success input_phone")
            self.pause(1)

            current_step = "input_password"
            self.input_password(password)
            self.log_step("【7】success input_password")
            self.pause(1)

            current_step = "click_login_button"
            self.click_login_button()
            self.log_step("【8】success click_login_button")
            self.debug_page_state("after_click_login_button")

        except Exception as exc:
            logger.exception("登录流程执行失败，失败步骤: %s", current_step)
            self.debug_page_state(f"login_exception_{current_step}", save_screenshot=True)
            self.log_step(f"【ERROR】卡在步骤 {current_step}，具体错误: {exc}")
            raise
