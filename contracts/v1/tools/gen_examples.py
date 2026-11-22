r"""生成 contracts/v1/examples 下的模拟响应。

确定性：无随机数，重跑输出一致。
一致性：脚本末尾对份额、对称矩阵、相似列表自检，失败即退出。

用法：.\.venv\Scripts\python.exe contracts\v1\tools\gen_examples.py
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_VERSION = "mock-v1"
SCHEMA_VERSION = "1.0"
SHA_PREFIX = "a1b2c3d4e5f6"
EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

# ---------------------------------------------------------------- 基础工具


def envelope(data, scope, filters=None):
    return {
        "schema_version": SCHEMA_VERSION,
        "data_version": DATA_VERSION,
        "meta": {
            "scope": scope,
            "filters": filters if scope == "filtered" else None,
            "duplicate_policy": "keep_all",
            "salary_unit": "K",
            "salary_basis": "quoted_range_midpoint",
        },
        "data": data,
    }


def no_filters():
    return {
        "city": [],
        "job_title": [],
        "company_type": [],
        "education": [],
        "experience": [],
        "salary_min": None,
        "salary_max": None,
    }


def filters(**overrides):
    base = no_filters()
    base.update(overrides)
    return base


def share(count, denominator):
    return round(count / denominator, 6)


# ---------------------------------------------------------------- 类别与地区

CITIES = ["F047", "P949", "R005", "A123", "B456", "C789"]
JOBS = ["J001", "J002", "J003", "J004", "J005"]
INDUSTRIES = ["I01", "I02", "I03", "I04", "I05"]
EDUCATIONS = ["ED", "GI", "MD"]
EXPERIENCES = ["EX1", "EX2", "EX3"]

JOB_TOTALS = {"J001": 420, "J002": 300, "J003": 180, "J004": 80, "J005": 35}

# city, total, company_count, salary_valid_count, salary
REGION_ROWS = [
    ("F047", 400, 120, 360, {"q1": 5.0, "median": 7.5, "q3": 10.0, "min": 2.0, "max": 30.0}),
    ("P949", 250, 80, 220, {"q1": 4.5, "median": 6.5, "q3": 9.0, "min": 2.0, "max": 25.0}),
    ("R005", 180, 60, 0, None),
    ("A123", 100, 30, 90, {"q1": 5.5, "median": 8.0, "q3": 11.0, "min": 3.0, "max": 28.0}),
    ("B456", 70, 22, 60, {"q1": 4.0, "median": 6.0, "q3": 8.5, "min": 2.5, "max": 20.0}),
    ("C789", 15, 8, 12, {"q1": 3.5, "median": 5.0, "q3": 6.5, "min": 2.0, "max": 9.0}),
]

TOTAL_RECORDS = sum(row[1] for row in REGION_ROWS)
TOTAL_VALID = sum(row[3] for row in REGION_ROWS)
COMPANY_COUNT = 288  # 去重后企业数，不等于各地区之和
SAMPLE_THRESHOLD = 30


def region_stats(row):
    city, total, companies, valid, salary = row
    return {
        "city": city,
        "total_records": total,
        "company_count": companies,
        "salary_valid_count": valid,
        "salary": salary,
        "small_sample": valid < SAMPLE_THRESHOLD,
    }


def region_items(rows):
    ordered = sorted(rows, key=lambda r: (-r[1], r[0]))
    return [region_stats(row) for row in ordered]


# ---------------------------------------------------------------- 明细记录

# row, job, city, exp, edu, company, industry, raw, lower, upper, mid, unit, months, status, dup
RECORDS = [
    (2, "J001", "F047", "EX1", "GI", "C001", "I01", "5-6K", 5.0, 6.0, 5.5, "K", None, "valid_range", False),
    (3, "J001", "F047", "EX2", "ED", "C002", "I01", "8-12K·13薪", 8.0, 12.0, 10.0, "K", 13, "valid_range", False),
    (4, "J002", "P949", "EX1", "GI", "C003", "I02", "6-9K", 6.0, 9.0, 7.5, "K", None, "valid_range", False),
    (5, "J003", "R005", "EX3", "MD", "C004", "I03", None, None, None, None, None, None, "missing", False),
    (6, "J001", "F047", "EX1", "GI", "C005", "I01", "面议", None, None, None, None, None, "unparsed", False),
    (7, "J002", "P949", "EX2", "ED", "C006", "I02", "12-8K", 12.0, 8.0, None, "K", None, "invalid_range", False),
    (8, "J004", "A123", "EX1", "GI", "C007", "I04", "8千-1.2万/月", None, None, None, "other", None, "unsupported_unit", False),
    (9, "J001", "F047", "EX1", "GI", "C008", "I01", "15K以上", 15.0, None, None, "K", None, "one_sided", False),
    (10, "J005", "B456", "EX2", "ED", "C009", "I05", "4-5K·14薪", 4.0, 5.0, 4.5, "K", 14, "valid_range", False),
    (11, "J001", "F047", "EX1", "GI", "C001", "I01", "5-6K", 5.0, 6.0, 5.5, "K", None, "valid_range", True),
    (12, "J002", "P949", "EX1", "GI", "C010", "I02", "7-9K", 7.0, 9.0, 8.0, "K", None, "valid_range", False),
    (13, "J003", "R005", "EX3", "MD", "C011", "I03", "9-11K", 9.0, 11.0, 10.0, "K", None, "valid_range", False),
    (14, "J004", "A123", "EX1", "GI", "C012", "I04", "10-15K", 10.0, 15.0, 12.5, "K", None, "valid_range", False),
    (15, "J005", "B456", "EX2", "ED", "C013", "I05", "3.5-4.5K", 3.5, 4.5, 4.0, "K", None, "valid_range", False),
    (16, "J001", "F047", "EX2", "ED", "C014", "I01", "6-8K·12薪", 6.0, 8.0, 7.0, "K", 12, "valid_range", False),
    (17, "J002", "P949", "EX1", "GI", None, "I02", "6-7K", 6.0, 7.0, 6.5, "K", None, "valid_range", False),
    (18, "J003", "R005", "EX3", "MD", "C015", "I03", "面议", None, None, None, None, None, "unparsed", False),
    (19, "J004", "A123", "EX1", "GI", "C016", "I04", "20-30K", 20.0, 30.0, 25.0, "K", None, "valid_range", False),
    (20, "J005", "B456", "EX2", "ED", "C017", "I05", None, None, None, None, None, None, "missing", False),
    (21, "J001", "F047", "EX1", "GI", "C018", "I01", "11-13K·15薪", 11.0, 13.0, 12.0, "K", 15, "valid_range", False),
]


def record(row):
    (source_row, job, city, exp, edu, company, industry, raw,
     lower, upper, mid, unit, months, status, dup) = row
    return {
        "record_id": f"{SHA_PREFIX}:second_data:{source_row}",
        "source_row": source_row,
        "job_title": job,
        "city": city,
        "experience": exp,
        "education": edu,
        "company": company,
        "company_type": industry,
        "salary_raw": raw,
        "salary_lower": lower,
        "salary_upper": upper,
        "salary_mid": mid,
        "salary_unit": unit,
        "pay_months": months,
        "salary_status": status,
        "is_extra_duplicate": dup,
    }


def last_page_records():
    """末页 15 条：总 1015 条、每页 20 → 第 51 页共 15 条。"""
    rows = []
    for offset in range(15):
        source_row = 1002 + offset
        job = JOBS[offset % len(JOBS)]
        city = CITIES[offset % len(CITIES)]
        rows.append((
            source_row, job, city, EXPERIENCES[offset % 3], EDUCATIONS[offset % 3],
            f"C{100 + offset:03d}", INDUSTRIES[offset % 5], "6-8K",
            6.0, 8.0, 7.0, "K", None, "valid_range", False,
        ))
    return [record(row) for row in rows]


# ---------------------------------------------------------------- 差异与相似

DIMENSIONS = ["industry", "region", "education", "experience", "salary"]
WEIGHTS = {name: 0.2 for name in DIMENSIONS}

DISTANCE_PAIRS = [
    ("J001", "J002", 0.50, 0.35, 0.45, 0.40, 0.40),
    ("J001", "J003", 0.40, 0.25, 0.30, 0.30, 0.30),
    ("J002", "J003", 0.60, 0.50, 0.55, 0.55, 0.55),
]

SIMILAR_TO_F047 = [
    ("P949", 0.86),
    ("A123", 0.79),
    ("R005", 0.74),
    ("B456", 0.68),
    ("C789", 0.61),
]


def distance_data():
    jobs = ["J001", "J002", "J003"]
    components = []
    totals = {}
    for left, right, *dims in DISTANCE_PAIRS:
        values = dict(zip(DIMENSIONS, dims))
        total = round(sum(dims) / len(DIMENSIONS), 6)
        totals[(left, right)] = totals[(right, left)] = total
        components.append({"left": left, "right": right, **values, "total": total})

    matrix = []
    for row_job in jobs:
        matrix.append([0.0 if row_job == col_job else totals[(row_job, col_job)] for col_job in jobs])

    return {
        "job_titles": jobs,
        "matrix": matrix,
        "components": components,
        "method": {
            "name": "weighted_tv_distance",
            "version": "1.0",
            "dimensions": DIMENSIONS,
            "weights": WEIGHTS,
            "salary_reference": {"lower": 2.0, "upper": 28.0},
            "reference_scope": "global",
            "min_salary_samples": 30,
        },
        "analysis_version": DATA_VERSION,
    }


def similar_data():
    totals = {row[0]: row[1] for row in REGION_ROWS}
    return {
        "city": "F047",
        "items": [
            {"city": city, "similarity": sim, "total_records": totals[city]}
            for city, sim in SIMILAR_TO_F047
        ],
        "method": "1 - TV(P‖Q)；基于全局行业发布结构，不含薪资项，不随页面筛选重算",
        "analysis_version": DATA_VERSION,
    }


# ---------------------------------------------------------------- 元信息与画像

FIELD_DOCS = [
    ("record_id", "string", False, None, "本数据版本内唯一的记录标识"),
    ("source_row", "integer", False, None, "Excel 1-based 行号，首条数据为 2"),
    ("job_title", "string", True, None, "职位类别代码，不是招聘记录 ID"),
    ("city", "string", True, None, "地区代码，不能解读为真实城市名"),
    ("experience", "string", True, None, "经验类别代码，无序"),
    ("education", "string", True, None, "学历类别代码，无序"),
    ("company", "string", True, None, "企业代码，无真实企业名"),
    ("company_type", "string", True, None, "行业类别代码，不是企业规模或所有制"),
    ("salary_raw", "string", True, None, "原始薪资文本，不被派生字段覆盖"),
    ("salary_lower", "number", True, "K", "报价下界"),
    ("salary_upper", "number", True, "K", "报价上界"),
    ("salary_mid", "number", True, "K", "报价中点，仅 valid_range 有值"),
    ("salary_unit", "string", True, None, "K 或 other；主统计只用 K"),
    ("pay_months", "integer", True, "月", "文本明确给出的几薪，未注明为 null"),
    ("salary_status", "string", False, None, "薪资解析状态枚举"),
    ("is_extra_duplicate", "boolean", False, None, "七原始字段完全相同的非首次记录"),
]

META_FIELDS = [
    {
        "name": name,
        "data_type": dtype,
        "nullable": nullable,
        "unit": unit,
        "description": description,
    }
    for name, dtype, nullable, unit, description in FIELD_DOCS
]

PROFILE_CITY_ITEMS = [("F047", 300), ("P949", 70), ("R005", 30), ("A123", 15), ("B456", 5)]
PROFILE_INDUSTRY_ITEMS = [("I01", 168), ("I02", 105), ("I03", 84), ("I04", 42), ("I05", 21)]
PROFILE_EDUCATION_ITEMS = [("GI", 210), ("ED", 126), ("MD", 63), (None, 21)]
PROFILE_EXPERIENCE_ITEMS = [("EX1", 252), ("EX2", 126), ("EX3", 42)]


def distribution(items, denominator):
    if denominator == 0:
        return {"denominator": 0, "items": []}
    return {
        "denominator": denominator,
        "items": [
            {"value": value, "count": count, "share": share(count, denominator)}
            for value, count in items
        ],
    }


# ---------------------------------------------------------------- 输出


def build():
    files = {}

    files["meta.json"] = envelope(
        {
            "fields": META_FIELDS,
            "filter_options": {
                "city": [{"value": c, "label": c} for c in sorted(CITIES)],
                "company_type": [{"value": i, "label": i} for i in INDUSTRIES],
                "education": [{"value": e, "label": e} for e in EDUCATIONS],
                "experience": [{"value": x, "label": x} for x in EXPERIENCES],
            },
            "capabilities": {
                "real_names": False,
                "geo": False,
                "time_series": False,
                "skills": False,
            },
            "analysis_version": DATA_VERSION,
            "distance_candidates": [{"value": j, "label": j} for j in JOBS],
            "sample_threshold": SAMPLE_THRESHOLD,
        },
        scope="global",
    )

    files["options.jobs.json"] = envelope(
        {
            "items": [{"job_title": j, "label": j, "total_records": JOB_TOTALS[j]} for j in JOBS],
            "page": 1,
            "page_size": 20,
            "total": len(JOBS),
        },
        scope="global",
    )

    overview = {
        "total_records": TOTAL_RECORDS,
        "company_count": COMPANY_COUNT,
        "job_count": len(JOBS),
        "salary_valid_count": TOTAL_VALID,
        "salary_median": 7.5,
    }
    files["overview.normal.json"] = envelope(overview, scope="filtered", filters=no_filters())

    empty_condition = filters(
        city=["C789"], job_title=["J005"], company_type=["I05"], education=["MD"], experience=["EX3"]
    )
    files["overview.empty.json"] = envelope(
        {
            "total_records": 0,
            "company_count": 0,
            "job_count": 0,
            "salary_valid_count": 0,
            "salary_median": None,
        },
        scope="filtered",
        filters=empty_condition,
    )

    files["regions.normal.json"] = envelope(
        {"items": region_items(REGION_ROWS)}, scope="filtered", filters=no_filters()
    )

    no_salary_rows = [row for row in REGION_ROWS if row[0] in ("R005", "C789")]
    files["regions.no_salary.json"] = envelope(
        {"items": region_items(no_salary_rows)}, scope="filtered", filters=no_filters()
    )

    denominator = JOB_TOTALS["J001"]
    files["profile.normal.json"] = envelope(
        {
            "job_title": "J001",
            "label": "J001",
            "total_records": denominator,
            "salary": {
                "valid_count": 380,
                "q1": 5.0,
                "median": 7.5,
                "q3": 10.5,
                "min": 2.0,
                "max": 30.0,
            },
            "distributions": {
                "city": distribution(PROFILE_CITY_ITEMS, denominator),
                "company_type": distribution(PROFILE_INDUSTRY_ITEMS, denominator),
                "education": distribution(PROFILE_EDUCATION_ITEMS, denominator),
                "experience": distribution(PROFILE_EXPERIENCE_ITEMS, denominator),
            },
        },
        scope="filtered",
        filters=filters(job_title=["J001"]),
    )

    files["profile.empty.json"] = envelope(
        {
            "job_title": "J005",
            "label": "J005",
            "total_records": 0,
            "salary": None,
            "distributions": {
                "city": distribution([], 0),
                "company_type": distribution([], 0),
                "education": distribution([], 0),
                "experience": distribution([], 0),
            },
        },
        scope="filtered",
        filters=filters(job_title=["J005"], education=["MD"], experience=["EX3"]),
    )

    files["records.page1.json"] = envelope(
        {
            "items": [record(row) for row in RECORDS],
            "page": 1,
            "page_size": 20,
            "total": TOTAL_RECORDS,
        },
        scope="filtered",
        filters=no_filters(),
    )

    files["records.last_page.json"] = envelope(
        {
            "items": last_page_records(),
            "page": 51,
            "page_size": 20,
            "total": TOTAL_RECORDS,
        },
        scope="filtered",
        filters=no_filters(),
    )

    files["distance.normal.json"] = envelope(
        distance_data(), scope="global"
    )
    files["similar.normal.json"] = envelope(
        similar_data(), scope="global"
    )

    files["error.validation.json"] = {
        "error": {
            "code": "INVALID_QUERY",
            "message": "salary_min 不能大于 salary_max",
            "details": [{"field": "salary_min", "reason": "out_of_range"}],
            "request_id": "req-6a1f3c22",
        }
    }
    files["error.not_ready.json"] = {
        "error": {
            "code": "DATA_NOT_READY",
            "message": "清洗数据尚未加载，请先运行导入脚本",
            "details": [],
            "request_id": "req-9b2d4e10",
        }
    }
    return files


def check(files):
    """一致性自检，任一不满足即抛错，避免把坏样例提交上去。"""
    regions = files["regions.normal.json"]["data"]["items"]
    assert sum(r["total_records"] for r in regions) == TOTAL_RECORDS
    assert sum(r["salary_valid_count"] for r in regions) == TOTAL_VALID
    assert [r["total_records"] for r in regions] == sorted(
        (r["total_records"] for r in regions), reverse=True
    )

    profile = files["profile.normal.json"]["data"]
    for name, dist in profile["distributions"].items():
        assert dist["denominator"] == profile["total_records"], name
        assert sum(item["count"] for item in dist["items"]) == dist["denominator"], name
        total_share = sum(item["share"] for item in dist["items"])
        assert abs(total_share - 1.0) <= 1e-5, (name, total_share)
        for item in dist["items"]:
            assert 0.0 <= item["share"] <= 1.0

    distance = files["distance.normal.json"]["data"]
    matrix = distance["matrix"]
    size = len(distance["job_titles"])
    assert len(matrix) == size and all(len(row) == size for row in matrix)
    for i in range(size):
        assert matrix[i][i] == 0.0
        for j in range(size):
            assert matrix[i][j] == matrix[j][i]
    for component in distance["components"]:
        assert abs(component["total"] - (sum(component[d] for d in DIMENSIONS) / 5)) <= 1e-6

    similar = files["similar.normal.json"]["data"]
    assert similar["city"] not in [item["city"] for item in similar["items"]]
    similarities = [item["similarity"] for item in similar["items"]]
    assert similarities == sorted(similarities, reverse=True)

    for item in files["records.page1.json"]["data"]["items"]:
        if item["salary_status"] == "valid_range" and item["salary_unit"] == "K":
            expected = (item["salary_lower"] + item["salary_upper"]) / 2
            assert abs(item["salary_mid"] - expected) <= 1e-9, item["record_id"]
        else:
            assert item["salary_mid"] is None, item["record_id"]


def main():
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    files = build()
    check(files)
    for name, payload in sorted(files.items()):
        path = EXAMPLES / name
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {path.relative_to(EXAMPLES.parents[2])}")
    print(f"{len(files)} 个样例已生成并通过一致性自检")


if __name__ == "__main__":
    main()
