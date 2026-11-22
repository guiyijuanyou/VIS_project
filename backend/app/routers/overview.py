"""GET /api/v1/overview（契约 6.4）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.envelope import Envelope
from ..core.envelope import filtered as filtered_response
from ..core.filters import FILTER_KEYS, FiltersDep, reject_unknown
from ..schemas import OverviewData
from ..services.repository import DatasetState, get_state
from ..services.repository import overview as load_overview

router = APIRouter()


@router.get("/overview", response_model=Envelope[OverviewData], summary="总量概览")
def get_overview(
    filters: FiltersDep,
    _: None = Depends(reject_unknown(*FILTER_KEYS)),
    state: DatasetState = Depends(get_state),
) -> Envelope[OverviewData]:
    return filtered_response(load_overview(state, filters), filters, state.data_version)
