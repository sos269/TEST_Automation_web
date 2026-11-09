"""示例测试（需要真实浏览器，默认被 -m 'not browser' 跳过）。

运行：pytest tests/test_example.py -m browser
"""
import pytest

from pages.example_pages import LoginPage
from webauto.core.base_test import BaseTest
from webauto.utils.config_loader import get_base_url


@pytest.mark.browser
class TestLoginExample(BaseTest):
    def setup_method(self):
        self.login = LoginPage(self.driver)

    def test_open_login_page(self):
        self.login.open(get_base_url() + LoginPage.url)
        assert self.driver.get_title().strip() != ""

    def test_login_button_visible(self):
        self.login.open(get_base_url() + LoginPage.url)
        assert self.driver.is_visible(LoginPage.SUBMIT)
