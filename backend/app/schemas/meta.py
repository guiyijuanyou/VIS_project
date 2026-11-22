"""GET /api/v1/meta 的响应数据（契约 6.2）。"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .common import CodeOption


class FieldDoc(BaseModel):
    name: str
    data_type: str
    nullable: bool
    unit: str | None = None
    description: str


class FilterOptions(BaseModel):
    city: list[CodeOption]
    company_type: list[CodeOption]
    education: list[CodeOption]
    experience: list[CodeOption]


class Capabilities(BaseModel):
    """固定能力声明：本项目没有这些数据，界面上不能造。"""

    real_names: bool = False
    geo: bool = False
    time_series: bool = False
    skills: bool = False


class MetaData(BaseModel):
    fields: list[FieldDoc]
    filter_options: FilterOptions
    capabilities: Capabilities
    analysis_version: str | None = Field(
        default=None, description="算法结果版本；未加载时为 null"
    )
    distance_candidates: list[CodeOption] | None = Field(
        default=None, description="可参与差异度计算的职位；未加载时为 null"
    )
    sample_threshold: int = Field(
        default=30, description="有效薪资低于该值的对象不进主排名，仅作展示提示"
    )
