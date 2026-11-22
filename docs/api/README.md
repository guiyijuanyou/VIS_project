# docs/api（人员二 B）

接口契约与快照。**字段与路径的唯一依据是 `contract.md`**，其他文件都是它的派生物。

| 文件 | 说明 |
|---|---|
| `contract.md` | v1 接口契约（H0 冻结）。参数、字段、枚举、错误格式、分页、作用域 |
| `openapi.json` | 由后端代码导出的 OpenAPI 快照，供前端离线对齐类型 |
| `../../contracts/v1/examples/` | 14 个 `mock-v1` 模拟响应 |
| `../../contracts/v1/acceptance_cases.json` | 12 条三人共用的集成用例 |

## 重新导出 OpenAPI

```powershell
.\.venv\Scripts\python.exe -c "import json;from backend.app.main import app;open('docs/api/openapi.json','w',encoding='utf-8').write(json.dumps(app.openapi(),ensure_ascii=False,indent=2,sort_keys=True)+'\n')"
```

改了路由或模型后必须重导，否则前端拿到的类型是旧的。

## 待决事项

- **CC-001**：`/regions` 是否提供地区行业结构（`top_industries` 或独立 compare 接口）。需三人确认后才能实现，详见 `contract.md` 第 12 节。
- **CC-002**：`sample_threshold`、`distance_candidates`、`label` 三个可选字段已实现，属通知级变更。
