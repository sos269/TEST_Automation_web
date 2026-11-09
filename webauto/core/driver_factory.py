"""浏览器驱动工厂。

将 Playwright 封装为引擎无关的高层 Driver，AI 生成的用例只依赖这套
稳定的高层 API（open / click / type / get_text ...），从而：
  1. 生成的用例不耦合具体引擎，未来可平滑替换为 Selenium；
  2. 用例可读性高，便于人工审阅与二次编辑。
"""
from playwright.sync_api import Page, sync_playwright

from webauto.utils.config_loader import load_config
from webauto.utils.logger import get_logger

logger = get_logger(__name__)


class Driver:
    """高层、引擎无关的浏览器操作封装。"""

    def __init__(self, page: Page, playwright=None, browser=None, context=None):
        self._page = page
        self._playwright = playwright
        self._browser = browser
        self._context = context

    # ---- 导航 ----
    def open(self, url: str):
        logger.info("打开页面: %s", url)
        self._page.goto(url, wait_until="domcontentloaded")

    # ---- 交互 ----
    def click(self, selector: str):
        logger.info("点击: %s", selector)
        self._page.click(selector)

    def type(self, selector: str, text: str):
        logger.info("在 %s 输入: %s", selector, text)
        self._page.fill(selector, text)

    def hover(self, selector: str):
        self._page.hover(selector)

    # ---- 读取 ----
    def get_text(self, selector: str) -> str:
        return self._page.text_content(selector) or ""

    def get_title(self) -> str:
        return self._page.title()

    def get_current_url(self) -> str:
        return self._page.url

    # ---- 断言辅助 ----
    def wait_for(self, selector: str, timeout: int = None):
        self._page.wait_for_selector(selector, timeout=timeout)

    def is_visible(self, selector: str) -> bool:
        try:
            return self._page.is_visible(selector)
        except Exception:
            return False

    # ---- 其他 ----
    def screenshot(self, path: str):
        self._page.screenshot(path=path)
        logger.info("截图已保存: %s", path)

    @property
    def page(self) -> Page:
        return self._page

    def close(self):
        try:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as e:  # noqa: BLE001
            logger.warning("关闭驱动时发生异常: %s", e)


def create_driver(browser_type: str = None, headless: bool = None) -> Driver:
    """根据配置创建并启动一个浏览器 Driver。"""
    cfg = load_config()
    btype = browser_type or cfg["browser"]["type"]
    is_headless = headless if headless is not None else cfg["browser"].get("headless", True)
    timeout_ms = int(cfg["browser"].get("timeout", 30)) * 1000
    viewport = cfg["browser"].get("viewport")

    playwright = sync_playwright().start()
    browser = getattr(playwright, btype).launch(headless=is_headless)
    context = browser.new_context(viewport=viewport)
    page = context.new_page()
    page.set_default_timeout(timeout_ms)

    logger.info("启动浏览器 %s (headless=%s)", btype, is_headless)
    return Driver(page, playwright=playwright, browser=browser, context=context)
