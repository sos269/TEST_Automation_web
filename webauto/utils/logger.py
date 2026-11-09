"""统一日志：控制台 + 文件（reports/test.log）。"""
import logging
import os

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def get_logger(name="webauto"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(_FORMAT)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    try:
        os.makedirs("reports", exist_ok=True)
        fh = logging.FileHandler("reports/test.log", encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        # 日志落盘失败不应阻断测试
        pass
    return logger
