"""GET /api/v1/meta（契约 6.2）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.envelope import Envelope, global_scope
from ..core.filters import reject_unknown
from ..schemas import MetaData
from ..services.repository import DatasetState, get_state
from ..services.repository import meta as load_meta

router = APIRouter()


@router.get("/meta", response_model=Envelope[MetaData], summary="元信息与筛选选项")
def get_meta(
    _: None = Depends(reject_unknown()),
    state: DatasetState = Depends(get_state),
) -> Envelope[MetaData]:
    return global_scope(load_meta(state), state.data_version)
