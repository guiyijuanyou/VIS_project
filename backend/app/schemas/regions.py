"""地区页与相似地区的响应数据（契约 6.5、6.9）。"""

from __future__ import annotations

from pydantic import Field

from .common import SalaryQuantiles, StrictModel


class RegionStats(StrictModel):
    city: str
    total_records: int = Field(ge=0, description="发布记录数，分母不因薪资无效而减少")
    company_count: int = Field(ge=0)
    salary_valid_count: int = Field(ge=0)
    salary: SalaryQuantiles | None = Field(
        default=None, description="五数概括；无有效薪资时整体为 null"
    )
    small_sample: bool = Field(description="salary_valid_count < 30")


class RegionsData(StrictModel):
    items: list[RegionStats]


class SimilarRegionItem(StrictModel):
    city: str
    similarity: float = Field(ge=0, le=1)
    total_records: int = Field(ge=0)


class SimilarRegionsData(StrictModel):
    city: str
    items: list[SimilarRegionItem]
    method: str = Field(description="固定说明：1-TV，基于全局行业发布结构，不含薪资")
    analysis_version: str
