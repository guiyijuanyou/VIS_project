"""GET /api/v1/regions、/api/v1/regions/similar（契约 6.5、6.9）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.envelope import Envelope, global_scope
from ..core.envelope import filtered as filtered_response
from ..core.filters import (
    FILTER_KEYS,
    FiltersDep,
    SimilarDep,
    reject_unknown,
    require_exactly_one,
)
from ..schemas import RegionsData, SimilarRegionsData
from ..services.repository import DatasetState, get_state
from ..services.repository import regions as load_regions
from ..services.repository import similar as load_similar

router = APIRouter()


@router.get("/regions", response_model=Envelope[RegionsData], summary="地区比较")
def get_regions(
    filters: FiltersDep,
    _: None = Depends(reject_unknown(*FILTER_KEYS)),
    state: DatasetState = Depends(get_state),
) -> Envelope[RegionsData]:
    return filtered_response(load_regions(state, filters), filters, state.data_version)


@router.get(
    "/regions/similar",
    response_model=Envelope[SimilarRegionsData],
    summary="相似地区（全局基线）",
)
def get_similar_regions(
    query: SimilarDep,
    _: None = Depends(reject_unknown("city", "limit")),
    state: DatasetState = Depends(get_state),
) -> Envelope[SimilarRegionsData]:
    city = require_exactly_one(query.city, "city")
    return global_scope(load_similar(state, city, query.limit), state.data_version)
