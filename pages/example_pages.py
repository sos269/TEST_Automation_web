"""示例页面对象：登录页。展示如何用 POM 封装页面与业务动作。"""
from webauto.core.base_page import BasePage


class LoginPage(BasePage):
    url = "/login"

    USERNAME = "input[name='username']"
    PASSWORD = "input[name='password']"
    SUBMIT = "button[type='submit']"
    ERROR = ".error-message"

    def login(self, username: str, password: str):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def get_error(self) -> str:
        return self.get_text(self.ERROR)
