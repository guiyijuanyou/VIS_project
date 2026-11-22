"""GET /api/v1/records 的响应数据（契约 6.7）。

Record 字段严格对应数据契约 3.2，不额外发一套 Parquet 行号字段。
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .common import SalaryStatus, StrictModel


class Record(StrictModel):
    record_id: str
    source_row: int = Field(ge=2, description="Excel 1-based 行号，首条数据为 2")
    job_title: str | None = None
    city: str | None = None
    experience: str | None = None
    education: str | None = None
    company: str | None = None
    company_type: str | None = None
    salary_raw: str | None = Field(default=None, description="原始文本，不被派生字段覆盖")
    salary_lower: float | None = None
    salary_upper: float | None = None
    salary_mid: float | None = Field(default=None, description="仅 valid_range 有值")
    salary_unit: str | None = None
    pay_months: int | None = None
    salary_status: SalaryStatus
    is_extra_duplicate: bool


class RecordsData(StrictModel):
    items: list[Record]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0, description="过滤后全部记录数，不是当前页条数")
