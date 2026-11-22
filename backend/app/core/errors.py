"""统一错误格式（契约第 3 节）。

框架默认的校验错误必须在这里被改写，否则前端要兼容两套结构。
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Iterable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("vis.api")

_REQUEST_ID_FALLBACK = "req-unknown"

_REASON_BY_TYPE = {
    "missing": "missing",
    "greater_than_equal": "out_of_range",
    "greater_than": "out_of_range",
    "less_than_equal": "out_of_range",
    "less_than": "out_of_range",
    "too_long": "too_many",
    "string_too_long": "too_many",
}


class ErrorCode(str, Enum):
    INVALID_QUERY = "INVALID_QUERY"
    NOT_FOUND = "NOT_FOUND"
    DATA_NOT_READY = "DATA_NOT_READY"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    field: str
    reason: str


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    """业务可预期的错误，带固定 code；不要继承 ValueError。"""

    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: Iterable[tuple[str, str]] | Iterable[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details: list[ErrorDetail] = [_as_detail(item) for item in (details or [])]


def _as_detail(item: tuple[str, str] | ErrorDetail) -> ErrorDetail:
    if isinstance(item, ErrorDetail):
        return item
    field, reason = item
    return ErrorDetail(field=field, reason=reason)


def invalid_query(
    message: str, details: Iterable[tuple[str, str]] | None = None
) -> AppError:
    return AppError(422, ErrorCode.INVALID_QUERY, message, details)


def not_found(message: str, field: str | None = None) -> AppError:
    details = [(field, "not_found")] if field else None
    return AppError(404, ErrorCode.NOT_FOUND, message, details)


def data_not_ready(message: str) -> AppError:
    return AppError(503, ErrorCode.DATA_NOT_READY, message)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", _REQUEST_ID_FALLBACK)


def _error_response(
    request: Request,
    status_code: int,
    code: ErrorCode,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorBody(
            code=code,
            message=message,
            details=details or [],
            request_id=_request_id(request),
        )
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _reason_for(error_type: str) -> str:
    if error_type in _REASON_BY_TYPE:
        return _REASON_BY_TYPE[error_type]
    if error_type.endswith(("_parsing", "_type", "_error")):
        return "invalid"
    return "invalid"


def _field_for(location: tuple[object, ...]) -> str:
    parts = [str(part) for part in location]
    if parts and parts[0] in {"query", "body", "path", "header", "cookie"}:
        parts = parts[1:]
    return ".".join(parts) or "request"


def _validation_details(exc: RequestValidationError) -> list[ErrorDetail]:
    details: list[ErrorDetail] = []
    seen: set[tuple[str, str]] = set()
    for error in exc.errors():
        detail = ErrorDetail(
            field=_field_for(tuple(error.get("loc", ()))),
            reason=_reason_for(str(error.get("type", "invalid"))),
        )
        key = (detail.field, detail.reason)
        if key not in seen:
            seen.add(key)
            details.append(detail)
    return details


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("app error %s: %s (request_id=%s)", exc.code, exc.message, _request_id(request))
        return _error_response(request, exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = _validation_details(exc)
        fields = "、".join(detail.field for detail in details) or "查询参数"
        return _error_response(
            request,
            422,
            ErrorCode.INVALID_QUERY,
            f"参数校验失败：{fields}",
            details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        if exc.status_code == 404:
            code, message = ErrorCode.NOT_FOUND, "请求的路径或对象不存在"
        elif 400 <= exc.status_code < 500:
            code, message = ErrorCode.INVALID_QUERY, str(exc.detail)
        else:
            code, message = ErrorCode.INTERNAL_ERROR, "服务内部错误"
        return _error_response(request, exc.status_code, code, message)

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        # 堆栈、文件路径、SQL 只进日志，不进响应。
        logger.exception("unexpected error (request_id=%s)", _request_id(request))
        return _error_response(
            request, 500, ErrorCode.INTERNAL_ERROR, "服务内部错误，请查看服务日志"
        )
