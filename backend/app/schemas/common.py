"""跨接口共用的响应片段。"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """禁止 NaN / Infinity：契约要求不可用数值一律 null。"""

    model_config = ConfigDict(allow_inf_nan=False)


class SalaryStatus(str, Enum):
    VALID_RANGE = "valid_range"
    MISSING = "missing"
    UNPARSED = "unparsed"
    INVALID_RANGE = "invalid_range"
    UNSUPPORTED_UNIT = "unsupported_unit"
    ONE_SIDED = "one_sided"


class SalaryUnit(str, Enum):
    K = "K"
    OTHER = "other"


class CodeOption(BaseModel):
    value: str
    label: str


class ShareItem(StrictModel):
    value: str | None = Field(description="原代码；未知类别为 null")
    count: int = Field(ge=0)
    share: float = Field(ge=0, le=1)


class Distribution(StrictModel):
    denominator: int = Field(ge=0)
    items: list[ShareItem]


class SalaryQuantiles(StrictModel):
    """五数概括，不是 1.5IQR 异常值箱线图。"""

    q1: float | None = None
    median: float | None = None
    q3: float | None = None
    min: float | None = None
    max: float | None = None


class SalarySummary(SalaryQuantiles):
    valid_count: int = Field(ge=0)
