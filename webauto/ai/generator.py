"""AI 测试用例生成器。

两种模式：
  - 模板模式（离线）：基于 URL/描述做启发式推理，生成冒烟/功能用例，
    无需任何 API Key，开箱即用；
  - LLM 模式：调用 OpenAI 兼容接口，由大模型分析站点并生成用例。

无论哪种模式，最终都渲染为使用 webauto 高层 API 的标准 pytest 文件，
可被框架直接执行。
"""
import json
import os
import re
from urllib.parse import urlparse

from webauto.ai.prompts import GENERATE_PROMPT, SYSTEM_PROMPT
from webauto.utils.config_loader import load_config
from webauto.utils.logger import get_logger

logger = get_logger(__name__)

_IND = "    "


class AITestGenerator:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.ai_cfg = self.config.get("ai", {}) or {}

    # ------------------------------------------------------------------ #
    # 入口
    # ------------------------------------------------------------------ #
    def generate(self, site_url: str, description: str = "", use_llm: bool = None):
        """返回用例列表（dict 组成的 list）。"""
        if use_llm is None:
            env_key = os.environ.get("AI_API_KEY")
            cfg_key = self.ai_cfg.get("api_key", "")
            use_llm = bool(env_key) or (bool(cfg_key) and not cfg_key.startswith("${"))

        if use_llm:
            try:
                logger.info("使用 LLM 生成测试用例 ...")
                return self._generate_with_llm(site_url, description)
            except Exception as e:  # noqa: BLE001
                logger.warning("LLM 生成失败（%s），回退到模板生成。", e)
        logger.info("使用模板（离线）生成测试用例 ...")
        return self._generate_template(site_url, description)

    # ------------------------------------------------------------------ #
    # 模板模式
    # ------------------------------------------------------------------ #
    def _generate_template(self, site_url: str, description: str = ""):
        domain = urlparse(site_url).netloc or site_url
        parts = domain.split(".")
        keyword = parts[-2] if len(parts) >= 2 else domain

        cases = [
            {
                "id": "TC001",
                "title": f"打开 {domain} 首页并验证页面加载",
                "priority": "P0",
                "steps": [
                    {"action": "open", "target": "BASE_URL"},
                    {"action": "assert_title_not_empty"},
                    {"action": "assert_element_visible", "selector": "body"},
                ],
            },
            {
                "id": "TC002",
                "title": "验证页面标题包含站点关键字",
                "priority": "P1",
                "steps": [
                    {"action": "open", "target": "BASE_URL"},
                    {"action": "assert_title_contains", "value": keyword},
                ],
            },
            {
                "id": "TC003",
                "title": "验证核心导航/页脚存在",
                "priority": "P1",
                "steps": [
                    {"action": "open", "target": "BASE_URL"},
                    {"action": "assert_element_visible", "selector": "header, nav"},
                    {"action": "assert_element_visible", "selector": "footer"},
                ],
            },
        ]

        desc = description or ""
        if "login" in desc.lower() or "登录" in desc:
            cases.append({
                "id": "TC004",
                "title": "验证登录表单元素存在",
                "priority": "P1",
                "steps": [
                    {"action": "open", "target": "BASE_URL"},
                    {"action": "assert_element_visible",
                     "selector": "input[type='text'], input[type='email'], "
                                 "input[name*='user'], input[name*='email']"},
                    {"action": "assert_element_visible",
                     "selector": "input[type='password']"},
                ],
            })
        if "search" in desc.lower() or "搜索" in desc:
            cases.append({
                "id": "TC005",
                "title": "验证搜索框存在",
                "priority": "P2",
                "steps": [
                    {"action": "open", "target": "BASE_URL"},
                    {"action": "assert_element_visible",
                     "selector": "input[type='search'], input[name*='search'], "
                                 "input[placeholder*='搜索']"},
                ],
            })
        return cases

    # ------------------------------------------------------------------ #
    # LLM 模式
    # ------------------------------------------------------------------ #
    def _generate_with_llm(self, site_url: str, description: str):
        import requests

        api_key = os.environ.get("AI_API_KEY") or self.ai_cfg.get("api_key")
        if not api_key or api_key.startswith("${"):
            raise RuntimeError("未配置 AI API Key")

        base_url = self.ai_cfg.get("base_url", "https://api.openai.com/v1").rstrip("/")
        model = self.ai_cfg.get("model", "gpt-4o-mini")
        temperature = self.ai_cfg.get("temperature", 0.3)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": GENERATE_PROMPT.format(site_url=site_url, description=description or "（无额外描述）")},
        ]
        payload = {"model": model, "temperature": temperature, "messages": messages}
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        resp = requests.post(f"{base_url}/chat/completions", headers=headers,
                             json=payload, timeout=120)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return self._parse_llm_cases(content)

    @staticmethod
    def _parse_llm_cases(content: str):
        """从模型返回中提取 JSON，兼容被 markdown 代码块包裹的情况。"""
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(text[start:end + 1])
            else:
                raise
        cases = data.get("test_cases") or data.get("cases") or []
        if not isinstance(cases, list):
            raise ValueError("LLM 返回结构异常：test_cases 应为数组")
        return cases

    # ------------------------------------------------------------------ #
    # 渲染
    # ------------------------------------------------------------------ #
    def render_test_file(self, cases, site_url: str, class_name: str = "TestAIGenerated") -> str:
        lines = [
            '"""',
            f"由 webauto AITestGenerator 自动生成的 Web 自动化测试用例",
            f"目标站点: {site_url}",
            '"""',
            "import pytest",
            "",
            "from webauto.core.driver_factory import create_driver",
            "",
            f'BASE_URL = "{site_url}"',
            "",
            "",
            "@pytest.mark.browser",
            f"class {class_name}:",
            f"{_IND}@pytest.fixture(autouse=True)",
            f"{_IND}def _setup(self):",
            f"{_IND}{_IND}self.driver = create_driver()",
            f"{_IND}{_IND}yield",
            f"{_IND}{_IND}self.driver.close()",
            "",
        ]
        for case in cases:
            lines.extend(self._render_method(case))
            lines.append("")
        return "\n".join(lines)

    def _render_method(self, case: dict):
        cid = re.sub(r"\W+", "_", str(case.get("id", "tc")).lower())
        title = case.get("title", "")
        priority = case.get("priority", "")
        out = [
            f"{_IND}def test_{cid}(self):",
            f'{_IND}{_IND}"""{title} [priority {priority}]"""',
        ]
        for step in case.get("steps", []):
            out.append(f"{_IND}{_IND}{self._render_step(step)}")
        return out

    @staticmethod
    def _render_step(step: dict) -> str:
        action = step.get("action", "")
        if action == "open":
            return f"self.driver.open({step.get('target', 'BASE_URL')})"
        if action == "click":
            return f"self.driver.click({step['selector']!r})"
        if action == "type":
            return f"self.driver.type({step['selector']!r}, {step.get('value', '')!r})"
        if action == "wait":
            return f"self.driver.wait_for({step['selector']!r})"
        if action == "hover":
            return f"self.driver.hover({step['selector']!r})"
        if action == "assert_title_contains":
            return f"assert {step.get('value', '')!r} in self.driver.get_title()"
        if action == "assert_title_not_empty":
            return "assert self.driver.get_title().strip() != ''"
        if action == "assert_element_visible":
            sel = step["selector"]
            return f'assert self.driver.is_visible({sel!r}), "expected visible: {sel}"'
        if action == "assert_text":
            return f"assert {step.get('value', '')!r} in self.driver.get_text({step['selector']!r})"
        return f"# 未知动作: {action}"

    # ------------------------------------------------------------------ #
    # 落盘
    # ------------------------------------------------------------------ #
    def write_test_file(self, cases, site_url: str, out_path: str, class_name: str = "TestAIGenerated") -> str:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        content = self.render_test_file(cases, site_url, class_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("已写出 %d 条用例 -> %s", len(cases), out_path)
        return out_path
