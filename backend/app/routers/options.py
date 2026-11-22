"""GET /api/v1/options/jobs（契约 6.3）。"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..core.envelope import Envelope, global_scope
from ..core.filters import PAGING_KEYS, PagingDep, reject_unknown
from ..schemas import JobOptionsData
from ..services.repository import DatasetState, get_state
from ..services.repository import job_options as load_job_options

router = APIRouter()


@router.get(
    "/options/jobs",
    response_model=Envelope[JobOptionsData],
    summary="职位代码搜索与分页",
)
def get_job_options(
    paging: PagingDep,
    q: Annotated[str | None, Query(description="对原代码做字面子串匹配，区分大小写")] = None,
    _: None = Depends(reject_unknown(*PAGING_KEYS, "q")),
    state: DatasetState = Depends(get_state),
) -> Envelope[JobOptionsData]:
    data = load_job_options(state, q, paging.page, paging.page_size)
    return global_scope(data, state.data_version)
