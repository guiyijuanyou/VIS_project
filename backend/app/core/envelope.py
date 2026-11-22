"""统一成功响应外壳（契约第 2 节）。

除 health 外所有 2xx 响应都必须套这一层，前端在 client.ts 一处拆壳。
"""

from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from ..settings import DUPLICATE_POLICY, SALARY_BASIS, SALARY_UNIT, SCHEMA_VERSION


class FilterSet(BaseModel):
    """规范化后的筛选条件，回填到 meta.filters。"""

    city: list[str] = Field(default_factory=list)
    job_title: list[str] = Field(default_factory=list)
    company_type: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    salary_min: float | None = None
    salary_max: float | None = None


class MetaBlock(BaseModel):
    scope: Literal["filtered", "global"]
    filters: FilterSet | None
    duplicate_policy: Literal["keep_all"] = DUPLICATE_POLICY  # type: ignore[assignment]
    salary_unit: Literal["K"] = SALARY_UNIT  # type: ignore[assignment]
    salary_basis: Literal["quoted_range_midpoint"] = SALARY_BASIS  # type: ignore[assignment]


DataT = TypeVar("DataT")


class Envelope(BaseModel, Generic[DataT]):
    schema_version: str = SCHEMA_VERSION
    data_version: str
    meta: MetaBlock
    data: DataT


def filtered(data: DataT, filters: FilterSet, data_version: str) -> Envelope[DataT]:
    return Envelope[DataT](
        data_version=data_version,
        meta=MetaBlock(scope="filtered", filters=filters),
        data=data,
    )


def global_scope(data: DataT, data_version: str) -> Envelope[DataT]:
    """固定全局基线：meta.filters 必须为 null，避免被读成跟随筛选。"""
    return Envelope[DataT](
        data_version=data_version,
        meta=MetaBlock(scope="global", filters=None),
        data=data,
    )
