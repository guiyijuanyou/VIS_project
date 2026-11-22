"""GET /api/v1/jobs/profile、/api/v1/jobs/distance（契约 6.6、6.8）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.envelope import Envelope, global_scope
from ..core.envelope import filtered as filtered_response
from ..core.filters import (
    FILTER_KEYS,
    FiltersDep,
    JobTitlesDep,
    reject_unknown,
    require_between,
    require_exactly_one,
)
from ..schemas import JobDistanceData, JobProfileData
from ..services.repository import DatasetState, get_state
from ..services.repository import distance as load_distance
from ..services.repository import profile as load_profile

router = APIRouter()


@router.get(
    "/jobs/profile",
    response_model=Envelope[JobProfileData],
    summary="职位画像",
)
def get_job_profile(
    filters: FiltersDep,
    _: None = Depends(reject_unknown(*FILTER_KEYS)),
    state: DatasetState = Depends(get_state),
) -> Envelope[JobProfileData]:
    job_title = require_exactly_one(filters.job_title, "job_title")
    data = load_profile(state, filters, job_title)
    return filtered_response(data, filters, state.data_version)


@router.get(
    "/jobs/distance",
    response_model=Envelope[JobDistanceData],
    summary="职位差异度（全局基线）",
)
def get_job_distance(
    job_titles: JobTitlesDep,
    _: None = Depends(reject_unknown("job_title")),
    state: DatasetState = Depends(get_state),
) -> Envelope[JobDistanceData]:
    selected = require_between(job_titles, "job_title", 2, 4)
    return global_scope(load_distance(state, selected), state.data_version)
