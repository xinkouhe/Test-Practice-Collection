#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
整体规划较小，未给tests设置子模块
"""

import pytest
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from pages.login_page import LoginPage
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DRIVER_PATH = PROJECT_ROOT / "utils" / "edgedriver_win64" / "msedgedriver.exe"

@pytest.fixture(scope="session", autouse=True)
def driver():
    service = EdgeService(executable_path=str(DRIVER_PATH))
    options = webdriver.EdgeOptions()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0')
    options.add_argument('--start-maximized')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Edge(service=service, options=options)
    yield driver
    driver.quit()

@pytest.fixture
def login_page(driver):
    return LoginPage(driver)

