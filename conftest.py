"""pytest 全局 fixtures。"""
import os

import pytest

from webauto.core.driver_factory import create_driver
from webauto.utils.config_loader import load_config


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=os.environ.get("WEB_AUTO_ENV", "default"),
                     help="运行环境：default/dev/test/prod")
    parser.addoption("--browser", action="store", default=None,
                     help="覆盖浏览器类型：chromium/firefox/webkit")


@pytest.fixture(scope="session")
def config():
    return load_config()


@pytest.fixture(scope="function")
def driver(request, config):
    """为每个测试函数提供一个浏览器 Driver（需真实浏览器）。"""
    browser_type = request.config.getoption("--browser") or config["browser"]["type"]
    headless = config["browser"].get("headless", True)
    d = create_driver(browser_type=browser_type, headless=headless)
    yield d
    d.close()
