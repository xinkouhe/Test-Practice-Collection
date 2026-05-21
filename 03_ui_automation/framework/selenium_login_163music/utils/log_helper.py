#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"
LOG_DIR = REPORT_DIR / "logs"
SCREENSHOT_DIR = REPORT_DIR / "screenshots"
RUN_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_LOG_PATH = LOG_DIR / f"run_{RUN_STAMP}.log"
LATEST_LOG_PATH = LOG_DIR / "latest.log"
LOGGER_NAME = "ui_test"


def ensure_report_dirs() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging() -> Path:
    ensure_report_dirs()

    logger = logging.getLogger(LOGGER_NAME)
    if getattr(logger, "_custom_configured", False):
        return RUN_LOG_PATH

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    for log_path in (RUN_LOG_PATH, LATEST_LOG_PATH):
        handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger._custom_configured = True
    logger.info("日志初始化完成，运行日志: %s", RUN_LOG_PATH)
    logger.info("日志初始化完成，最新日志: %s", LATEST_LOG_PATH)
    return RUN_LOG_PATH


def get_logger(name: str | None = None) -> logging.Logger:
    configure_logging()
    if not name:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def sanitize_name(name: str) -> str:
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", name).strip("_") or "artifact"


def save_driver_screenshot(driver, name: str) -> Path | None:
    ensure_report_dirs()
    file_name = f"{sanitize_name(name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screenshot_path = SCREENSHOT_DIR / file_name

    if driver.save_screenshot(str(screenshot_path)):
        return screenshot_path
    return None
