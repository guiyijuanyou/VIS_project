"""GET /api/v1/health（契约 6.1）。

不套响应外壳，也不要求数据库已加载：用于区分“进程活了”与“数据没好”。
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ..settings import API_VERSION

router = APIRouter()


class HealthData(BaseModel):
    status: str = "ok"
    api_version: str = API_VERSION


@router.get("/health", response_model=HealthData, summary="服务状态")
def get_health() -> HealthData:
    return HealthData()
