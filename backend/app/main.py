r"""FastAPI 应用入口。

启动：.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
接口契约：docs/api/contract.md
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request

from .core.errors import register_error_handlers
from .routers import health, jobs, meta, options, overview, records, regions
from .settings import API_VERSION, allow_mock

app = FastAPI(
    title="职位画像与城市就业机会可视分析系统 API",
    version=API_VERSION,
    description=(
        "基于 ChinaVis 2024 虚拟招聘数据。地区与职位以代码展示，"
        "不提供真实名称、地理坐标、时间序列与技能字段。"
    ),
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url=None,
)

register_error_handlers(app)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request.state.request_id = f"req-{uuid.uuid4().hex[:8]}"
    return await call_next(request)


API_PREFIX = "/api/v1"

for module in (health, meta, options, overview, regions, jobs, records):
    app.include_router(module.router, prefix=API_PREFIX)


@app.get("/health", include_in_schema=False)
def health_alias() -> dict[str, str]:
    """探活别名，响应与 /api/v1/health 一致。"""
    return {"status": "ok", "api_version": API_VERSION}


__all__ = ["app", "allow_mock"]
