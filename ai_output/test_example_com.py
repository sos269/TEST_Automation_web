"""
由 webauto AITestGenerator 自动生成的 Web 自动化测试用例
目标站点: https://example.com
"""
import pytest

from webauto.core.driver_factory import create_driver

BASE_URL = "https://example.com"


@pytest.mark.browser
class TestAIGenerated:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.driver = create_driver()
        yield
        self.driver.close()

    def test_tc001(self):
        """打开 example.com 首页并验证页面加载 [priority P0]"""
        self.driver.open(BASE_URL)
        assert self.driver.get_title().strip() != ''
        assert self.driver.is_visible('body'), "expected visible: body"

    def test_tc002(self):
        """验证页面标题包含站点关键字 [priority P1]"""
        self.driver.open(BASE_URL)
        assert 'example' in self.driver.get_title()

    def test_tc003(self):
        """验证核心导航/页脚存在 [priority P1]"""
        self.driver.open(BASE_URL)
        assert self.driver.is_visible('header, nav'), "expected visible: header, nav"
        assert self.driver.is_visible('footer'), "expected visible: footer"

    def test_tc004(self):
        """验证登录表单元素存在 [priority P1]"""
        self.driver.open(BASE_URL)
        assert self.driver.is_visible("input[type='text'], input[type='email'], input[name*='user'], input[name*='email']"), "expected visible: input[type='text'], input[type='email'], input[name*='user'], input[name*='email']"
        assert self.driver.is_visible("input[type='password']"), "expected visible: input[type='password']"

    def test_tc005(self):
        """验证搜索框存在 [priority P2]"""
        self.driver.open(BASE_URL)
        assert self.driver.is_visible("input[type='search'], input[name*='search'], input[placeholder*='搜索']"), "expected visible: input[type='search'], input[name*='search'], input[placeholder*='搜索']"
