# -*- coding: utf-8 -*-
"""
旧脚本基线版。
保留原有流程和定位方式，减少非必要交互，并增加整轮重试。
"""

import logging
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.edge.service import Service as EdgeService


PROJECT_ROOT = Path(__file__).resolve().parent
REPORT_ROOT = PROJECT_ROOT / "reports" / "legacy_script"
LOG_DIR = REPORT_ROOT / "logs"
SCREENSHOT_DIR = REPORT_ROOT / "screenshots"
RUN_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = LOG_DIR / f"legacy_run_{RUN_STAMP}.log"
MAX_ATTEMPTS = 3
ATTEMPT_COOLDOWN_SECONDS = 5
AUTO_CLOSE_SECONDS = 3

LOGIN_LINK = (By.CSS_SELECTOR, ".m-tophead.f-pr.j-tflag a")
OTHER_LINK = (By.XPATH, '//a[contains(text(), "选择其他登录模式")]')
AGREEMENT_LINK = (By.XPATH, '//*[@id="j-official-terms"]')
PHONE_LINK = (By.XPATH, '//div[contains(text(), "手机号登录/注册")]')
PASSWORD_LINK = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/div[1]/a")
PHONE_INPUT = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[1]/div/input")
PASSWORD_INPUT = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[2]/div/input")
LOGIN_BUTTON = (By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div[2]/section/a/div")


def ensure_report_dirs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def build_logger():
    ensure_report_dirs()
    logger = logging.getLogger(f"legacy_script.{RUN_STAMP}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


LOGGER = build_logger()


def log(message):
    LOGGER.info(message)
    print(message)


def save_step_screenshot(driver, name):
    ensure_report_dirs()
    screenshot_path = SCREENSHOT_DIR / f"{RUN_STAMP}_{name}.png"
    try:
        if driver.save_screenshot(str(screenshot_path)):
            log(f"截图已保存: {screenshot_path}")
            return screenshot_path
        log(f"截图保存失败: {screenshot_path}")
    except Exception as exc:
        LOGGER.exception("保存截图失败: %s", name)
        print(f"保存截图失败: {name} -> {exc}")
    return None


def wait_find(driver, locator, desc, timeout=15, poll=0.5):
    deadline = time.time() + timeout
    last_error = None
    log(f"开始等待元素: {desc}, locator={locator}, timeout={timeout}s")

    while time.time() < deadline:
        try:
            elements = driver.find_elements(*locator)
            if elements:
                log(f"等待成功: {desc}, count={len(elements)}")
                return elements[0]
        except Exception as exc:
            last_error = exc
        time.sleep(poll)

    if last_error is not None:
        raise last_error
    raise TimeoutError(f"等待元素超时: {desc}, locator={locator}")


def js_click(driver, locator, desc, timeout=15):
    element = wait_find(driver, locator, desc, timeout=timeout)
    driver.execute_script("arguments[0].click();", element)
    log(f"点击成功: {desc}")


def input_text(driver, locator, text, desc, timeout=15):
    element = wait_find(driver, locator, desc, timeout=timeout)
    element.clear()
    if text is not None:
        element.send_keys(text)
    log(f"输入成功: {desc}")


def build_driver():
    service = EdgeService(
        executable_path=str(PROJECT_ROOT / "utils" / "edgedriver_win64" / "msedgedriver.exe")
    )
    options = webdriver.EdgeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
    )
    options.add_argument("--start-maximized")
    options.add_argument("--no-proxy-server")
    options.add_argument("--proxy-server=direct://")
    options.add_argument("--proxy-bypass-list=*")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    proxy = Proxy()
    proxy.proxy_type = ProxyType.DIRECT
    options.proxy = proxy

    driver = webdriver.Edge(service=service, options=options)
    if hasattr(driver.command_executor, "_client_config"):
        driver.command_executor._client_config.timeout = 15
    return service, driver


def run_once(attempt_no):
    service = None
    driver = None
    log(f"开始第 {attempt_no} 次尝试")
    try:
        service, driver = build_driver()
        driver.get("https://music.163.com")
        log("打开首页成功")
        time.sleep(2)

        save_step_screenshot(driver, f"attempt_{attempt_no}_home")
        js_click(driver, LOGIN_LINK, "click_login_link")
        js_click(driver, OTHER_LINK, "click_other_link")
        js_click(driver, AGREEMENT_LINK, "click_agreement_link")
        js_click(driver, PHONE_LINK, "click_phone_link")
        js_click(driver, PASSWORD_LINK, "click_password_link")

        input_text(driver, PHONE_INPUT, "", "input_phone")
        input_text(driver, PASSWORD_INPUT, "", "input_password")

        login_button = wait_find(driver, LOGIN_BUTTON, "click_login_button", timeout=15)
        login_button.click()
        log("点击成功: click_login_button")

        save_step_screenshot(driver, f"attempt_{attempt_no}_after_click_login_button")
        log(f"第 {attempt_no} 次尝试成功")
        time.sleep(AUTO_CLOSE_SECONDS)
        return True
    except Exception:
        LOGGER.exception("第 %s 次尝试失败", attempt_no)
        if driver is not None:
            save_step_screenshot(driver, f"attempt_{attempt_no}_legacy_exception")
        return False
    finally:
        if driver is not None:
            try:
                driver.quit()
                log("浏览器已关闭")
            except Exception:
                LOGGER.exception("关闭浏览器失败")
        if service is not None:
            try:
                service.stop()
            except Exception:
                LOGGER.exception("停止驱动服务失败")


def main():
    log(f"旧脚本开始执行，日志文件: {LOG_PATH}")

    for attempt_no in range(1, MAX_ATTEMPTS + 1):
        success = run_once(attempt_no)
        if success:
            log("旧脚本执行结束")
            return

        if attempt_no < MAX_ATTEMPTS:
            log(f"等待 {ATTEMPT_COOLDOWN_SECONDS} 秒后进入下一次尝试")
            time.sleep(ATTEMPT_COOLDOWN_SECONDS)

    raise RuntimeError(f"旧脚本连续重试 {MAX_ATTEMPTS} 次后仍失败")


if __name__ == "__main__":
    main()
