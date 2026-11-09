"""页面对象（POM）基类。

所有页面类继承 BasePage，封装该页面的定位符与业务动作，
使测试用例与页面结构解耦，也便于 AI 生成的用例复用。
"""
from webauto.core.driver_factory import Driver


class BasePage:
    # 子类可覆盖为页面路径，例如 "/login"
    url = None

    def __init__(self, driver: Driver):
        self.driver = driver

    def open(self, url: str = None):
        target = url or self.url
        if not target:
            raise ValueError("未指定打开地址：请传入 url 或在子类中定义 url")
        self.driver.open(target)

    def click(self, selector: str):
        self.driver.click(selector)

    def type(self, selector: str, text: str):
        self.driver.type(selector, text)

    def hover(self, selector: str):
        self.driver.hover(selector)

    def get_text(self, selector: str) -> str:
        return self.driver.get_text(selector)

    def wait_for(self, selector: str, timeout: int = None):
        self.driver.wait_for(selector, timeout)

    def is_visible(self, selector: str) -> bool:
        return self.driver.is_visible(selector)

    def screenshot(self, name: str):
        import os
        os.makedirs("reports/screenshots", exist_ok=True)
        self.driver.screenshot(f"reports/screenshots/{name}.png")
