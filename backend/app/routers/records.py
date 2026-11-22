"""GET /api/v1/records（契约 6.7）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.envelope import Envelope
from ..core.envelope import filtered as filtered_response
from ..core.filters import FILTER_KEYS, PAGING_KEYS, FiltersDep, PagingDep, reject_unknown
from ..schemas import RecordsData
from ..services.repository import DatasetState, get_state
from ..services.repository import records as load_records

router = APIRouter()


@router.get("/records", response_model=Envelope[RecordsData], summary="来源明细（分页）")
def get_records(
    filters: FiltersDep,
    paging: PagingDep,
    _: None = Depends(reject_unknown(*FILTER_KEYS, *PAGING_KEYS)),
    state: DatasetState = Depends(get_state),
) -> Envelope[RecordsData]:
    data = load_records(state, filters, paging.page, paging.page_size)
    return filtered_response(data, filters, state.data_version)
