"""AI 生成管线自测：无需浏览器即可验证「生成 + 渲染」正确可用。

运行：pytest tests/test_ai_generator.py -v
"""
import os
import tempfile

from webauto.ai.generator import AITestGenerator


def test_template_generation_and_render():
    gen = AITestGenerator()
    cases = gen.generate("https://example.com", "包含登录与搜索功能", use_llm=False)

    assert isinstance(cases, list) and len(cases) >= 3
    # 渲染为 Python 源码并能成功编译（语法正确）
    source = gen.render_test_file(cases, "https://example.com")
    compiled = compile(source, "<generated>", "exec")
    assert compiled is not None
    # 包含 BASE_URL 与至少一个测试方法
    assert "BASE_URL" in source
    assert "def test_" in source


def test_write_test_file(tmp_path=None):
    out = os.path.join(tempfile.gettempdir(), "webauto_gen_sample.py")
    gen = AITestGenerator()
    cases = gen.generate("https://example.com", use_llm=False)
    path = gen.write_test_file(cases, "https://example.com", out)
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    compile(content, path, "exec")  # 确保落盘文件可编译
