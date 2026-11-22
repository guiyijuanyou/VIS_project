"""数据访问层。

当前只实现模拟响应（`contracts/v1/examples`），真实查询在 B04/B05 接入 DuckDB 后替换
`_require_real_impl` 之后的分支。路由不关心数据来自哪里。
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache

from ..core.envelope import FilterSet
from ..core.errors import data_not_ready, not_found
from ..schemas import (
    DistanceComponent,
    Distribution,
    JobDistanceData,
    JobOptionItem,
    JobOptionsData,
    JobProfileData,
    MetaData,
    OverviewData,
    ProfileDistributions,
    Record,
    RecordsData,
    RegionStats,
    RegionsData,
    SimilarRegionItem,
    SimilarRegionsData,
)
from ..settings import (
    EXAMPLES_DIR,
    MOCK_DATA_VERSION,
    SAMPLE_THRESHOLD,
    allow_mock,
    real_data_ready,
    real_data_version,
)

REAL_IMPL_PENDING = (
    "真实统计查询尚未实现（B04/B05 里程碑）；"
    "当前请以 APP_ALLOW_MOCK=1 启动，用共享模拟响应做结构联调"
)


@dataclass(frozen=True)
class DatasetState:
    ready: bool
    use_mock: bool
    data_version: str


def get_state() -> DatasetState:
    """每个请求判定一次数据可用性，不做隐式回落。"""
    if real_data_ready():
        return DatasetState(ready=True, use_mock=False, data_version=real_data_version())
    if allow_mock():
        return DatasetState(ready=False, use_mock=True, data_version=MOCK_DATA_VERSION)
    raise data_not_ready(
        "清洗数据尚未加载，且未允许模拟响应；请先运行 backend/scripts/import_data.py"
    )


@lru_cache(maxsize=1)
def _examples() -> dict[str, dict]:
    if not EXAMPLES_DIR.is_dir():
        raise data_not_ready("缺少 contracts/v1/examples，请检查仓库完整性")
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in EXAMPLES_DIR.glob("*.json")
    }


def _data(name: str) -> dict:
    try:
        return _examples()[name]["data"]
    except KeyError as exc:  # pragma: no cover - 仓库缺文件时才会触发
        raise data_not_ready(f"缺少模拟样例 {name}.json") from exc


def _require_real_impl() -> None:
    raise data_not_ready(REAL_IMPL_PENDING)


def _empty_distribution() -> Distribution:
    return Distribution(denominator=0, items=[])


def meta(state: DatasetState) -> MetaData:
    if not state.use_mock:
        _require_real_impl()
    payload = dict(_data("meta"))
    payload["sample_threshold"] = SAMPLE_THRESHOLD
    return MetaData(**payload)


def job_options(
    state: DatasetState, q: str | None, page: int, page_size: int
) -> JobOptionsData:
    if not state.use_mock:
        _require_real_impl()
    items = [JobOptionItem(**item) for item in _data("options.jobs")["items"]]
    if q:
        items = [item for item in items if q in item.job_title]
    start = (page - 1) * page_size
    return JobOptionsData(
        items=items[start : start + page_size],
        page=page,
        page_size=page_size,
        total=len(items),
    )


def overview(state: DatasetState, filters: FilterSet) -> OverviewData:
    # 模拟响应固定返回全局数值：只证明结构与状态，不做语义聚合（契约第 9 节）。
    if not state.use_mock:
        _require_real_impl()
    return OverviewData(**_data("overview.normal"))


def regions(state: DatasetState, filters: FilterSet) -> RegionsData:
    if not state.use_mock:
        _require_real_impl()
    return RegionsData(items=[RegionStats(**item) for item in _data("regions.normal")["items"]])


def profile(state: DatasetState, filters: FilterSet, job_title: str) -> JobProfileData:
    if not state.use_mock:
        _require_real_impl()
    payload = _data("profile.normal")
    if job_title == payload["job_title"]:
        return JobProfileData(**payload)

    known = {item["job_title"] for item in _data("options.jobs")["items"]}
    if job_title not in known:
        raise not_found(f"职位代码 {job_title} 不存在", field="job_title")
    return JobProfileData(
        job_title=job_title,
        label=job_title,
        total_records=0,
        salary=None,
        distributions=ProfileDistributions(
            city=_empty_distribution(),
            company_type=_empty_distribution(),
            education=_empty_distribution(),
            experience=_empty_distribution(),
        ),
    )


def records(state: DatasetState, filters: FilterSet, page: int, page_size: int) -> RecordsData:
    if not state.use_mock:
        _require_real_impl()
    first = _data("records.page1")
    last = _data("records.last_page")
    total = first["total"]
    total_pages = math.ceil(total / page_size)

    if page == 1:
        items = [Record(**item) for item in first["items"][:page_size]]
    elif page == total_pages:
        items = [Record(**item) for item in last["items"][:page_size]]
    else:
        items = []
    return RecordsData(items=items, page=page, page_size=page_size, total=total)


def distance(state: DatasetState, job_titles: list[str]) -> JobDistanceData:
    if not state.use_mock:
        _require_real_impl()
    payload = _data("distance.normal")
    fixture = payload["job_titles"]
    missing = [title for title in job_titles if title not in fixture]
    if missing:
        raise not_found(
            "差异度基线不包含职位 " + "、".join(missing) + "；模拟模式仅支持 "
            + "、".join(fixture),
            field="job_title",
        )

    totals: dict[tuple[str, str], float] = {}
    for component in payload["components"]:
        left, right = component["left"], component["right"]
        totals[(left, right)] = totals[(right, left)] = component["total"]

    matrix = [
        [0.0 if row == column else totals[(row, column)] for column in job_titles]
        for row in job_titles
    ]
    components = [
        DistanceComponent(**component)
        for component in payload["components"]
        if component["left"] in job_titles and component["right"] in job_titles
    ]
    return JobDistanceData(
        job_titles=job_titles,
        matrix=matrix,
        components=components,
        method=payload["method"],
        analysis_version=payload["analysis_version"],
    )


def similar(state: DatasetState, city: str, limit: int) -> SimilarRegionsData:
    if not state.use_mock:
        _require_real_impl()
    payload = _data("similar.normal")
    known = {item["city"] for item in _data("regions.normal")["items"]}
    if city not in known:
        raise not_found(f"地区代码 {city} 不存在", field="city")

    items = [] if city != payload["city"] else [
        SimilarRegionItem(**item) for item in payload["items"][:limit]
    ]
    return SimilarRegionsData(
        city=city,
        items=items,
        method=payload["method"],
        analysis_version=payload["analysis_version"],
    )
