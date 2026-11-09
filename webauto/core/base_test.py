"""测试基类：统一注入 driver fixture。"""
import pytest

from webauto.core.driver_factory import Driver


class BaseTest:
    """测试用例继承此类即可通过 self.driver 访问浏览器。"""

    @pytest.fixture(autouse=True)
    def _inject_driver(self, driver: Driver):
        self.driver: Driver = driver
        yield
