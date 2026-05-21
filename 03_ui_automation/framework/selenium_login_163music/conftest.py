#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
整体规划较小，未给tests设置子模块
"""

import pytest
import subprocess
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.edge.service import Service as EdgeService
from pages.login_page import LoginPage
from pathlib import Path
from utils.log_helper import LATEST_LOG_PATH
from utils.log_helper import configure_logging
from utils.log_helper import get_logger
from utils.log_helper import save_driver_screenshot

PROJECT_ROOT = Path(__file__).parent
DRIVER_PATH = PROJECT_ROOT / "utils" / "edgedriver_win64" / "msedgedriver.exe"
PROFILE_ROOT = PROJECT_ROOT / ".runtime_profiles"
CASE_COOLDOWN_SECONDS = 5
configure_logging()
logger = get_logger(__name__)


def build_edge_options(profile_dir: Path):
    options = webdriver.EdgeOptions()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-proxy-server')
    options.add_argument('--proxy-server=direct://')
    options.add_argument('--proxy-bypass-list=*')
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])

    # 强制当前自动化会话直连，不继承系统或全局代理。
    proxy = Proxy()
    proxy.proxy_type = ProxyType.DIRECT
    options.proxy = proxy
    return options


def create_profile_dir() -> Path:
    PROFILE_ROOT.mkdir(parents=True, exist_ok=True)
    profile_dir = PROFILE_ROOT / f"profile_{int(time.time() * 1000)}"
    profile_dir.mkdir(parents=True, exist_ok=True)
    logger.info("创建独立浏览器环境: %s", profile_dir)
    return profile_dir


def kill_edge_processes_by_profile(profile_dir: Path) -> None:
    profile_arg = str(profile_dir).replace("'", "''")
    command = (
        f"$profilePath = '{profile_arg}'; "
        "Get-CimInstance Win32_Process -Filter \"Name = 'msedge.exe'\" | "
        "Where-Object { $_.CommandLine -like \"*${profilePath}*\" } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def cleanup_profile_dir(profile_dir: Path) -> None:
    if profile_dir.exists():
        try:
            shutil.rmtree(profile_dir, ignore_errors=False)
            logger.info("已清理独立浏览器环境: %s", profile_dir)
        except Exception:
            logger.exception("清理独立浏览器环境失败: %s", profile_dir)


def pytest_configure(config):
    logger.info("pytest 启动，最新日志文件: %s", LATEST_LOG_PATH.resolve())


def pytest_runtest_setup(item):
    logger.info("开始执行用例: %s", item.nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        logger.info("用例执行结果: %s -> %s", item.nodeid, report.outcome)

    if report.failed:
        logger.error("用例失败阶段: %s -> %s", report.when, item.nodeid)
        logger.error("失败堆栈:\n%s", report.longreprtext)

        driver = item.funcargs.get("driver")
        # 当 driver 已经失联时，再去截图只会继续卡住 teardown。
        unstable_driver_markers = (
            "HTTPConnectionPool(host='localhost'",
            "Read timed out",
            "MaxRetryError",
            "timed out",
        )
        if driver is not None and not any(marker in report.longreprtext for marker in unstable_driver_markers):
            try:
                screenshot_path = save_driver_screenshot(driver, f"{item.nodeid}_{report.when}")
                if screenshot_path is not None:
                    logger.error("失败截图: %s", screenshot_path.resolve())
            except Exception:
                logger.exception("保存失败截图时出错")
        elif driver is not None:
            driver._skip_quit = True
            logger.warning("检测到 driver 已失联，本次失败跳过截图")


def pytest_sessionfinish(session, exitstatus):
    logger.info("pytest 结束，exitstatus=%s", exitstatus)

@pytest.fixture()
def driver():
    logger.info("准备启动 EdgeDriver: %s", DRIVER_PATH)
    service = EdgeService(executable_path=str(DRIVER_PATH))
    profile_dir = create_profile_dir()
    options = build_edge_options(profile_dir)
    driver = webdriver.Edge(service=service, options=options)
    if hasattr(driver.command_executor, "_client_config"):
        driver.command_executor._client_config.timeout = 30
    logger.info("Edge 会话已创建: %s", driver.session_id)
    yield driver
    service_pid = getattr(getattr(service, "process", None), "pid", None)
    if getattr(driver, "_skip_quit", False):
        logger.warning("本次跳过 driver.quit()，直接清理 EdgeDriver 进程")
    else:
        try:
            driver.quit()
            logger.info("Edge 会话已关闭: %s", driver.session_id)
        except Exception:
            logger.exception("关闭 Edge 会话失败: %s", getattr(driver, "session_id", "unknown"))
    try:
        kill_edge_processes_by_profile(profile_dir)
    except Exception:
        logger.exception("按独立浏览器环境清理 Edge 进程失败: %s", profile_dir)
    try:
        service.stop()
    except Exception:
        logger.exception("停止 EdgeDriver 服务失败")
    process = getattr(service, "process", None)
    if process is not None and process.poll() is None:
        logger.warning("EdgeDriver 进程仍存活，执行进程树清理: %s", process.pid)
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except Exception:
            logger.exception("进程树清理失败: %s", process.pid)
    elif service_pid is not None:
        logger.info("EdgeDriver 进程已结束: %s", service_pid)
    cleanup_profile_dir(profile_dir)
    logger.info("冷却 %s 秒后进入下一个 case", CASE_COOLDOWN_SECONDS)
    time.sleep(CASE_COOLDOWN_SECONDS)

@pytest.fixture
def login_page(driver):
    return LoginPage(driver)

