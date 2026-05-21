#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from utils.auto_load_csv import load_csv_rows

# 这个用例只跑负例数据，当前不会自动扫描其他 CSV。
@pytest.mark.parametrize("case", load_csv_rows("test_account_login.csv"))
def test_login_failure(driver, login_page, case):
    driver.get("https://music.163.com")
    assert {"phone", "password", "expected_error"} <= set(case)

    login_page.login(case["phone"], case["password"])

    em = login_page.get_error_message()
    assert case["expected_error"] in em
