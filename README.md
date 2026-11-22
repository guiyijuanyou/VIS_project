# 职位画像与城市就业机会可视分析系统

基于 ChinaVis 2024 虚拟招聘数据（430,664 条）的可视分析系统。**地区、职位、学历、经验、行业均以代码展示**，数据中没有真实名称、技能、发布时间与经纬度，因此系统不提供地理地图、时间趋势与适岗推荐。

## 目录与负责人

| 目录 | 负责人 | 内容 |
|---|---|---|
| `data/` | A 廖杰 | 原始数据（只读）与清洗输出 |
| `scripts/`、`config/` | A 廖杰 | 清洗、画像、差异与相似度计算 |
| `backend/` | **B 周士博** | FastAPI 服务、导入器 |
| `frontend/` | C 陶嘉义 | Vue + TypeScript + ECharts 界面 |
| `contracts/v1/` | **B 周士博** | 接口契约的模拟响应与验收用例 |
| `docs/api/` | **B 周士博** | 接口契约、OpenAPI 快照 |
| `tests/api/` | **B 周士博** | 接口测试 |

## 环境要求

| 项 | 版本 | 说明 |
|---|---|---|
| Python | **3.12** | 3.13/3.14 上 pandas、pyarrow、duckdb 的轮子尚不稳定，不要用 |
| Node.js | 22 LTS | 前端由 C 维护 |

## 后端启动

```powershell
Set-Location D:\VIS_project

# 1) 建虚拟环境（用 3.12 解释器；本机路径示例）
py -3.12 -m venv .venv
# 若 py -3.12 找不到，可直接指定解释器：
# "C:\Users\<you>\AppData\Roaming\uv\python\cpython-3.12.13-windows-x86_64-none\python.exe" -m venv .venv

# 2) 安装依赖
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3) 启动服务
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

启动后：

- 健康检查 <http://127.0.0.1:8000/api/v1/health> → `{"status":"ok","api_version":"1.0"}`
- 交互文档 <http://127.0.0.1:8000/docs>
- OpenAPI <http://127.0.0.1:8000/openapi.json>

## 前端启动

```powershell
Set-Location D:\VIS_project\frontend
npm ci
npm run dev   # 固定 5173，/api 代理到 127.0.0.1:8000
```

## 模拟数据与真实数据

后端有两种取数方式，**不会自动回落**：

| 场景 | 条件 | `data_version` |
|---|---|---|
| 结构联调 | 未导入清洗数据，且 `APP_ALLOW_MOCK=1`（默认） | `mock-v1` |
| 真实统计 | `data/processed/clean-v1/` 有 parquet 与 manifest | `clean-v1` |

```powershell
# 答辩与最终验收：必须关掉模拟，缺失数据要暴露成 503 而不是假装有数
$env:APP_ALLOW_MOCK="0"
```

前端用 `VITE_API_MODE=mock|real` 切换；real 模式请求失败时直接报错，不会退回模拟结果。

## 接口契约

- 契约正文：[`docs/api/contract.md`](docs/api/contract.md)（v1，H0 冻结）
- OpenAPI 快照：[`docs/api/openapi.json`](docs/api/openapi.json)
- 模拟响应：[`contracts/v1/examples/`](contracts/v1/examples)
- 集成用例：[`contracts/v1/acceptance_cases.json`](contracts/v1/acceptance_cases.json)

所有路径以 `/api/v1/` 开头，全部 GET，字段 `snake_case`，响应统一套 `{schema_version, data_version, meta, data}` 外壳（`health` 除外）。

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest
```

覆盖：外壳结构、422/404 统一错误格式、分页边界、全局基线作用域，以及 14 个模拟样例与 Pydantic 模型的一致性。

## 已知限制（不是缺陷）

1. **B04/B05 未完成**：真实数据的导入与统计查询尚未实现，请求真实数据会得到 503 `DATA_NOT_READY`。当前所有成功响应都来自 `mock-v1`。
2. `/regions` 暂不提供地区行业结构，C03 的行业占比比较需要先确认 CC-001（见契约第 12 节）。
3. `distance` 与 `similar` 是**全局基线**，不随页面筛选重算，接口会在 `meta.scope` 与文案里标明。

## 分支约定

`main` 只放可运行版本。开发用 `feat/data-*`（A）、`feat/api-*`（B）、`feat/ui-*`（C），提交信息用约定式：`<type>(<scope>): <简述>`。
