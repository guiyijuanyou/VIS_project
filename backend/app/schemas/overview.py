"""GET /api/v1/overview 的响应数据（契约 6.4）。"""

from __future__ import annotations

from pydantic import Field

from .common import StrictModel


class OverviewData(StrictModel):
    total_records: int = Field(ge=0)
    company_count: int = Field(ge=0)
    job_count: int = Field(ge=0)
    salary_valid_count: int = Field(ge=0)
    salary_median: float | None = Field(
        default=None, description="有效报价中点中位数；无有效样本时为 null"
    )
