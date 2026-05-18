#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from utils.auto_load_csv import load_csv_rows


@pytest.mark.parametrize("case", load_csv_rows("test_account_login.csv"))
def test_login_failure(driver, case):
    driver.get("https://music.163.com")

    # Each CSV row maps to one test case dictionary.
    assert {"phone", "password", "expected_error"} <= set(case)
