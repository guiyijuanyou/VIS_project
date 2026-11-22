"""筛选与分页解析（契约第 4 节、第 7 节）。

规则只在这里写一次，各接口通过 Depends 复用，不在路由里复制。
"""

from __future__ import annotations

import math
from typing import Annotated, Callable, Sequence

from fastapi import Depends, Query, Request
from pydantic import BaseModel, Field

from .envelope import FilterSet
from .errors import invalid_query

MAX_CODES_PER_FIELD = 50
MAX_PAGE_SIZE = 100

FILTER_KEYS = (
    "city",
    "job_title",
    "company_type",
    "education",
    "experience",
    "salary_min",
    "salary_max",
)
PAGING_KEYS = ("page", "page_size")


class FilterQuery(BaseModel):
    """通用筛选参数；重复键表达同字段 OR。"""

    city: list[str] = Field(default_factory=list)
    job_title: list[str] = Field(default_factory=list)
    company_type: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    salary_min: float | None = None
    salary_max: float | None = None


class PageQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=MAX_PAGE_SIZE)


class JobTitleQuery(BaseModel):
    job_title: list[str] = Field(default_factory=list)


class SimilarQuery(BaseModel):
    city: list[str] = Field(default_factory=list)
    limit: int = Field(5, ge=1, le=10)


def normalize_codes(field: str, values: Sequence[str]) -> list[str]:
    """去重、保序、保留大小写；空字符串与超量在这里拒绝。"""
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value == "":
            raise invalid_query(
                f"{field} 不能是空字符串，未使用时请不要传该参数",
                details=[(field, "empty")],
            )
        if value not in seen:
            seen.add(value)
            normalized.append(value)
    if len(normalized) > MAX_CODES_PER_FIELD:
        raise invalid_query(
            f"{field} 最多 {MAX_CODES_PER_FIELD} 个不同代码，当前 {len(normalized)} 个",
            details=[(field, "too_many")],
        )
    return normalized


def check_salary_range(salary_min: float | None, salary_max: float | None) -> None:
    for name, value in (("salary_min", salary_min), ("salary_max", salary_max)):
        if value is None:
            continue
        if not math.isfinite(value) or value < 0:
            raise invalid_query(
                f"{name} 必须是非负有限数", details=[(name, "out_of_range")]
            )
    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        raise invalid_query(
            "salary_min 不能大于 salary_max", details=[("salary_min", "out_of_range")]
        )


def _to_filter_set(query: FilterQuery) -> FilterSet:
    return FilterSet(
        city=normalize_codes("city", query.city),
        job_title=normalize_codes("job_title", query.job_title),
        company_type=normalize_codes("company_type", query.company_type),
        education=normalize_codes("education", query.education),
        experience=normalize_codes("experience", query.experience),
        salary_min=query.salary_min,
        salary_max=query.salary_max,
    )


def filters_dependency(query: Annotated[FilterQuery, Query()]) -> FilterSet:
    check_salary_range(query.salary_min, query.salary_max)
    return _to_filter_set(query)


def paging_dependency(query: Annotated[PageQuery, Query()]) -> PageQuery:
    return query


def job_titles_dependency(query: Annotated[JobTitleQuery, Query()]) -> list[str]:
    return normalize_codes("job_title", query.job_title)


def similar_dependency(query: Annotated[SimilarQuery, Query()]) -> SimilarQuery:
    return query.model_copy(update={"city": normalize_codes("city", query.city)})


FiltersDep = Annotated[FilterSet, Depends(filters_dependency)]
PagingDep = Annotated[PageQuery, Depends(paging_dependency)]
JobTitlesDep = Annotated[list[str], Depends(job_titles_dependency)]
SimilarDep = Annotated[SimilarQuery, Depends(similar_dependency)]


def reject_unknown(*allowed: str) -> Callable[[Request], None]:
    """顶层未知参数一律拒绝，防止把全局筛选误传给基线接口。"""

    allowed_set = frozenset(allowed)

    def dependency(request: Request) -> None:
        unknown = sorted({key for key in request.query_params.keys() if key not in allowed_set})
        if unknown:
            raise invalid_query(
                "存在未定义的查询参数：" + "、".join(unknown),
                details=[(key, "unknown_parameter") for key in unknown],
            )

    return dependency


def require_exactly_one(values: Sequence[str], field: str) -> str:
    if len(values) != 1:
        raise invalid_query(
            f"{field} 必须恰好传 1 个，当前 {len(values)} 个",
            details=[(field, "invalid_count")],
        )
    return values[0]


def require_between(values: Sequence[str], field: str, minimum: int, maximum: int) -> list[str]:
    if not minimum <= len(values) <= maximum:
        raise invalid_query(
            f"{field} 必须传 {minimum}～{maximum} 个，当前 {len(values)} 个",
            details=[(field, "invalid_count")],
        )
    return list(values)
