"""运行期配置。

不写死绝对路径：全部相对项目根目录推导，满足 G4「新环境按 README 可运行」。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_VERSION = "1.0"
API_VERSION = "1.0"

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed" / "clean-v1"
ANALYSIS_DIR = DATA_DIR / "processed" / "analysis-v1"
MANIFEST_PATH = PROCESSED_DIR / "manifest.json"

CONTRACTS_DIR = PROJECT_ROOT / "contracts" / "v1"
EXAMPLES_DIR = CONTRACTS_DIR / "examples"

MOCK_DATA_VERSION = "mock-v1"
DEFAULT_DATA_VERSION = "clean-v1"

DUPLICATE_POLICY = "keep_all"
SALARY_UNIT = "K"
SALARY_BASIS = "quoted_range_midpoint"
SAMPLE_THRESHOLD = 30


def allow_mock() -> bool:
    """是否允许在没有真实数据时返回模拟响应。

    答辩与最终验收必须 APP_ALLOW_MOCK=0，否则数据缺失会被静默掩盖（契约第 9 节）。
    """
    return os.environ.get("APP_ALLOW_MOCK", "1").strip() not in {"0", "false", "False", ""}


def real_data_version() -> str:
    """读取 manifest 里的 data_version；缺失时用默认值。"""
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return DEFAULT_DATA_VERSION
    return str(manifest.get("data_version") or DEFAULT_DATA_VERSION)


def real_data_ready() -> bool:
    return (PROCESSED_DIR / "jobs_clean.parquet").is_file() and MANIFEST_PATH.is_file()
