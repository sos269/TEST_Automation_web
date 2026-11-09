"""命令行入口：python -m webauto.cli <command>"""
import argparse
import sys

from webauto.ai.generator import AITestGenerator
from webauto.utils.config_loader import load_config
from webauto.utils.logger import get_logger

logger = get_logger("cli")


def _cmd_generate(args):
    cfg = load_config()
    gen = AITestGenerator(cfg)
    use_llm = None
    if args.llm:
        use_llm = True
    elif args.no_llm:
        use_llm = False
    cases = gen.generate(args.url, args.description, use_llm=use_llm)
    path = gen.write_test_file(cases, args.url, args.output)
    print(f"✅ 已生成 {len(cases)} 条测试用例 -> {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="webauto", description="WebAuto 网站自动化测试框架")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="根据站点自动生成 pytest 测试用例")
    gen.add_argument("--url", required=True, help="被测站点地址，如 https://example.com")
    gen.add_argument("--description", default="", help="补充说明（如：含登录、搜索功能）")
    gen.add_argument("--output", default="ai_output/test_generated.py", help="输出文件路径")
    gen.add_argument("--llm", action="store_true", help="强制使用 LLM 生成（需配置 API Key）")
    gen.add_argument("--no-llm", action="store_true", help="强制使用离线模板生成")

    args = parser.parse_args(argv)
    if args.command == "generate":
        _cmd_generate(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
