"""配置加载：YAML + 环境变量 ${VAR} 替换，带缓存。"""
import os
import re
from functools import lru_cache

import yaml

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _substitute(raw):
    if isinstance(raw, dict):
        return {k: _substitute(v) for k, v in raw.items()}
    if isinstance(raw, list):
        return [_substitute(v) for v in raw]
    if isinstance(raw, str):
        return _ENV_PATTERN.sub(
            lambda m: os.environ.get(m.group(1), m.group(0)), raw
        )
    return raw


def _project_root():
    # webauto/utils/config_loader.py -> 上溯三级到项目根
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


@lru_cache(maxsize=1)
def load_config(path=None):
    """加载 settings.yaml，并合并对应环境的 base_url。"""
    path = path or os.environ.get("WEB_AUTO_CONFIG") or os.path.join(
        _project_root(), "config", "settings.yaml"
    )
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg = _substitute(cfg)

    env = os.environ.get("WEB_AUTO_ENV")
    if env:
        env_path = os.path.join(_project_root(), "config", "environments.yaml")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                envs = yaml.safe_load(f) or {}
            env_cfg = _substitute(envs).get(env)
            if env_cfg:
                cfg["base_url"] = env_cfg.get("base_url", cfg.get("base_url"))
                if "headless" in env_cfg:
                    cfg.setdefault("browser", {})["headless"] = env_cfg["headless"]
    return cfg


def get_base_url():
    return load_config().get("base_url", "")
