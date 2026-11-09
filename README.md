# WebAuto —— Python 网站自动化测试框架

一个面向**网站 UI 测试**的轻量自动化框架，基于 Playwright 引擎，提供稳定的高层
API 与页面对象（POM）抽象，并内置 **AI 自动生成测试用例**能力（离线模板 + LLM 两种模式）。

## 特性

- 🚀 **现代引擎**：基于 Playwright，自动等待、稳定可靠，支持 Chromium/Firefox/WebKit。
- 🧩 **高层 API 抽象**：AI 生成的用例只依赖 `open/click/type/get_text/...` 等稳定接口，
  与具体引擎解耦，可读、可维护、易二次编辑。
- 📐 **POM 支持**：`BasePage` 封装页面定位符与业务动作，用例与页面结构解耦。
- 🤖 **AI 生成用例**：`AITestGenerator` 可根据站点 URL 自动产出 pytest 文件；
  未配置 API Key 时自动回退到「离线模板生成」，开箱即用。
- 🌐 **多环境**：`config/environments.yaml` + `--env` 切换 dev/test/prod 地址。
- 📊 **报告**：pytest-html 自带 HTML 报告（默认输出 `reports/report.html`）。

## 目录结构

```
TEST_Automation_web/
├── config/
│   ├── settings.yaml          # 全局配置（浏览器/AI/报告）
│   └── environments.yaml      # 多环境地址
├── webauto/
│   ├── core/                  # driver_factory / base_page / base_test
│   ├── utils/                 # config_loader / logger
│   ├── ai/                    # AITestGenerator + prompts
│   └── cli.py                 # 命令行入口
├── pages/                     # 页面对象（POM）
├── tests/                     # 测试用例
├── ai_output/                 # AI 自动生成的用例
├── conftest.py
├── pytest.ini
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装浏览器（首次）
playwright install chromium

# 3. 运行框架自带的 AI 生成管线自测（无需浏览器）
pytest tests/test_ai_generator.py -v

# 4. 运行真实浏览器用例（需安装浏览器）
pytest tests/test_example.py -m browser
```

## AI 自动生成测试用例

### 离线模板（无需 API Key）

```bash
python -m webauto.cli generate --url https://example.com \
    --description "包含登录和搜索功能" \
    --output ai_output/test_example.py
```

随后运行生成的用例：

```bash
pytest ai_output/test_example.py -m browser
```

### LLM 生成（需要 API Key）

在 `config/settings.yaml` 配置 `ai.api_key`（或设置环境变量 `AI_API_KEY`），
并可用任意 OpenAI 兼容接口：

```bash
export AI_API_KEY="sk-xxxx"
python -m webauto.cli generate --url https://example.com --llm
```

没有 Key 时框架会自动回退到模板生成，因此两条命令都能产出可执行用例。

## 编写自己的用例

```python
import pytest
from webauto.core.base_test import BaseTest
from webauto.utils.config_loader import get_base_url

@pytest.mark.browser
class TestSmoke(BaseTest):
    def test_title(self):
        self.driver.open(get_base_url())
        assert "Example" in self.driver.get_title()
```

## 扩展页面对象

```python
from webauto.core.base_page import BasePage

class LoginPage(BasePage):
    url = "/login"
    USERNAME = "input[name='username']"
    PASSWORD = "input[name='password']"

    def login(self, u, p):
        self.type(self.USERNAME, u)
        self.type(self.PASSWORD, p)
```

## 后续演进建议

- 接入 Allure 生成更丰富的可视化报告；
- 为 `Driver` 增加 Selenium 实现，实现引擎可插拔；
- 将 `AITestGenerator` 接入 CI，对每次上线的站点自动补全新用例；
- 基于历史失败用例做「缺陷回归用例」自动生成。
