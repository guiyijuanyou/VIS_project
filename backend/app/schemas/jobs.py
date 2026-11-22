"""职位页与差异度的响应数据（契约 6.3、6.6、6.8）。"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .common import Distribution, SalarySummary, StrictModel


class JobOptionItem(BaseModel):
    job_title: str
    label: str
    total_records: int = Field(ge=0)


class JobOptionsData(BaseModel):
    items: list[JobOptionItem]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)


class ProfileDistributions(BaseModel):
    """固定四个维度；分母均为 total_records，未知类别计入分母。"""

    city: Distribution
    company_type: Distribution
    education: Distribution
    experience: Distribution


class JobProfileData(StrictModel):
    job_title: str
    label: str
    total_records: int = Field(ge=0)
    salary: SalarySummary | None = None
    distributions: ProfileDistributions


class DistanceMethod(BaseModel):
    name: str
    version: str
    dimensions: list[str]
    weights: dict[str, float]
    salary_reference: dict[str, float]
    reference_scope: str
    min_salary_samples: int


class DistanceComponent(StrictModel):
    """i<j 的无序对，各维分量让界面能解释“为什么不同”。"""

    left: str
    right: str
    industry: float | None = None
    region: float | None = None
    education: float | None = None
    experience: float | None = None
    salary: float | None = None
    total: float


class JobDistanceData(StrictModel):
    job_titles: list[str]
    matrix: list[list[float | None]] = Field(description="对称矩阵，对角线为 0")
    components: list[DistanceComponent]
    method: DistanceMethod
    analysis_version: str
