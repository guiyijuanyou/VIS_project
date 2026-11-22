r"""契约形状测试：接口外壳、错误格式、分页边界、模拟样例与模型一致。

运行：.\.venv\Scripts\python.exe -m pytest
这些用例不依赖真实数据，属 B03/B07 的回归基线。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.envelope import Envelope
from backend.app.core.errors import ErrorResponse
from backend.app.main import app
from backend.app.schemas import (
    JobDistanceData,
    JobOptionsData,
    JobProfileData,
    MetaData,
    OverviewData,
    RecordsData,
    RegionsData,
    SimilarRegionsData,
)

EXAMPLES = Path(__file__).resolve().parents[2] / "contracts" / "v1" / "examples"

ENVELOPE_MODEL_BY_PREFIX = {
    "meta": MetaData,
    "options.jobs": JobOptionsData,
    "overview": OverviewData,
    "regions": RegionsData,
    "profile": JobProfileData,
    "records": RecordsData,
    "distance": JobDistanceData,
    "similar": SimilarRegionsData,
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _model_for(path: str):
    for prefix in sorted(ENVELOPE_MODEL_BY_PREFIX, key=len, reverse=True):
        if path.startswith(prefix):
            return ENVELOPE_MODEL_BY_PREFIX[prefix]
    raise AssertionError(f"未登记的样例文件：{path}")


def test_health_is_not_wrapped(client: TestClient) -> None:
    body = client.get("/api/v1/health").json()
    assert body == {"status": "ok", "api_version": "1.0"}
    assert client.get("/health").json() == body


def test_envelope_has_required_blocks(client: TestClient) -> None:
    body = client.get("/api/v1/overview").json()
    assert set(body) == {"schema_version", "data_version", "meta", "data"}
    assert body["schema_version"] == "1.0"
    assert body["meta"]["scope"] == "filtered"
    assert body["meta"]["duplicate_policy"] == "keep_all"
    assert body["meta"]["salary_unit"] == "K"


def test_filtered_response_echoes_filters(client: TestClient) -> None:
    body = client.get("/api/v1/overview?city=F047&city=P949&education=GI").json()
    assert body["meta"]["filters"]["city"] == ["F047", "P949"]
    assert body["meta"]["filters"]["education"] == ["GI"]


def test_global_response_has_null_filters(client: TestClient) -> None:
    for path in ("/api/v1/meta", "/api/v1/options/jobs"):
        body = client.get(path).json()
        assert body["meta"]["scope"] == "global"
        assert body["meta"]["filters"] is None


@pytest.mark.parametrize(
    ("path", "field", "reason"),
    [
        ("/api/v1/overview?bogus=1", "bogus", "unknown_parameter"),
        ("/api/v1/overview?page=2", "page", "unknown_parameter"),
        ("/api/v1/overview?city=", "city", "empty"),
        ("/api/v1/overview?salary_min=20&salary_max=10", "salary_min", "out_of_range"),
        ("/api/v1/overview?salary_min=-1", "salary_min", "out_of_range"),
        ("/api/v1/records?page_size=200", "page_size", "out_of_range"),
        ("/api/v1/jobs/profile", "job_title", "invalid_count"),
        ("/api/v1/jobs/distance?job_title=J001", "job_title", "invalid_count"),
        ("/api/v1/regions/similar?city=F047&city=P949", "city", "invalid_count"),
    ],
)
def test_invalid_query_uses_single_error_format(
    client: TestClient, path: str, field: str, reason: str
) -> None:
    response = client.get(path)
    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == "INVALID_QUERY"
    assert {"field": field, "reason": reason} in body["error"]["details"]
    assert body["error"]["request_id"].startswith("req-")


def test_error_body_leaks_nothing(client: TestClient) -> None:
    text = client.get("/api/v1/overview?salary_min=20&salary_max=10").text
    for leaked in ("Traceback", "site-packages", "D:\\\\"):
        assert leaked not in text


def test_not_found_is_404(client: TestClient) -> None:
    body = client.get("/api/v1/regions/similar?city=NOPE").json()
    assert body["error"]["code"] == "NOT_FOUND"


def test_records_pagination_bounds(client: TestClient) -> None:
    first = client.get("/api/v1/records?page=1&page_size=20").json()["data"]
    last = client.get("/api/v1/records?page=51&page_size=20").json()["data"]
    beyond = client.get("/api/v1/records?page=999&page_size=20").json()["data"]

    assert first["total"] == last["total"] == beyond["total"]
    assert len(first["items"]) == 20
    assert len(last["items"]) == 15
    assert beyond["items"] == []
    rows = [item["source_row"] for item in first["items"]]
    assert rows == sorted(rows)


def test_distance_matrix_is_symmetric(client: TestClient) -> None:
    data = client.get("/api/v1/jobs/distance?job_title=J002&job_title=J001").json()["data"]
    assert data["job_titles"] == ["J002", "J001"]
    matrix = data["matrix"]
    assert matrix[0][0] == matrix[1][1] == 0
    assert matrix[0][1] == matrix[1][0]
    component = data["components"][0]
    dims = ["industry", "region", "education", "experience", "salary"]
    assert abs(component["total"] - sum(component[d] for d in dims) / 5) <= 1e-9


def test_similar_excludes_self(client: TestClient) -> None:
    data = client.get("/api/v1/regions/similar?city=F047&limit=3").json()["data"]
    assert data["city"] == "F047"
    assert len(data["items"]) == 3
    assert all(item["city"] != "F047" for item in data["items"])
    scores = [item["similarity"] for item in data["items"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("path", sorted(p.name for p in EXAMPLES.glob("*.json")))
def test_examples_match_models(path: str) -> None:
    payload = json.loads((EXAMPLES / path).read_text(encoding="utf-8"))
    if path.startswith("error."):
        ErrorResponse.model_validate(payload)
        return
    Envelope[_model_for(path)].model_validate(payload)


@pytest.mark.parametrize("path", sorted(p.name for p in EXAMPLES.glob("*.json")))
def test_examples_are_labelled_mock(path: str) -> None:
    payload = json.loads((EXAMPLES / path).read_text(encoding="utf-8"))
    if path.startswith("error."):
        return
    assert payload["data_version"] == "mock-v1"
