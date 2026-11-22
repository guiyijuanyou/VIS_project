# 接口契约 v1：后端与前端唯一实现依据

状态：**v1 冻结（H0）**　编写：周士博（B）　对应基线：`协作契约_V1.md` 第 4～5 节

本文件把协作契约的接口部分落成可直接编码的形式：路径、参数名、字段名、枚举、错误格式、分页规则。
配套的模拟响应在 `contracts/v1/examples/`，验收用例在 `contracts/v1/acceptance_cases.json`。

## 0. 效力与改动流程

1. **语义**（口径、分母、去重、单位、作用域）以 `协作契约_V1.md` 为准；**字段名、路径、枚举字面量**以本文件为准。两者若矛盾，先提 `contract-change`，不要自行取舍。
2. 任何改字段、单位、参数、分母、作用域的变更，按协作契约第 9 节走：写旧规则、新规则、原因、受影响模块、迁移方法 → 三人确认 → 先改本文件与 `examples/`，再改代码。
3. 本文件冻结后，前端类型文件（`frontend/src/api/types.ts`）必须与本文件一致；**后端不提供兼容旧命名的第二套字段**。
4. 破坏性变更用 v2；小规模新增可选字段只需通知（见第 12 节 CC-002）。

## 1. 路径与连接

| 项 | 约定 |
|---|---|
| 后端地址 | `http://127.0.0.1:8000` |
| 路径前缀 | 全部 `/api/v1/`（替代手册旧示例的 `/api/`） |
| 健康检查 | `GET /api/v1/health`，另提供同义别名 `GET /health` 供脚本探活，响应完全一致 |
| OpenAPI | `/openapi.json`，交互文档 `/docs` |
| 前端开发端口 | `5173`，`vite.config.ts` 把 `/api` 代理到 8000 |
| 方法 | 全部 `GET`。V1 无写接口、无账号、无权限 |
| CORS | 不开。开发期前端走同源代理，不需要跨域 |
| 尾斜杠 | 不加。`/api/v1/overview/` 视为未知路径 |

## 2. 成功响应外壳

除 `health` 外，所有 2xx 响应统一包裹：

```json
{
  "schema_version": "1.0",
  "data_version": "clean-v1",
  "meta": {
    "scope": "filtered",
    "filters": {"city": [], "job_title": [], "company_type": [], "education": [], "experience": [], "salary_min": null, "salary_max": null},
    "duplicate_policy": "keep_all",
    "salary_unit": "K",
    "salary_basis": "quoted_range_midpoint"
  },
  "data": {}
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | string | 固定 `"1.0"`，与 `data.schema.json` 对应 |
| `data_version` | string | 真实数据为 `clean-v1`；模拟响应必须是 `mock-v1` |
| `meta.scope` | `"filtered"` \| `"global"` | 该响应的统计口径范围 |
| `meta.filters` | object \| null | 实际生效的规范化条件；`global` 时为 `null` |
| `meta.duplicate_policy` | `"keep_all"` | V1 唯一取值，前端不提供切换 |
| `meta.salary_unit` | `"K"` | 薪资单位，界面原样展示 |
| `meta.salary_basis` | `"quoted_range_midpoint"` | 薪资口径为报价区间中点 |

`health` 例外，只返回 `{"status":"ok","api_version":"1.0"}`，不套外壳，不要求数据库已加载。

`meta.filters` 是**规范化后**的条件：已去重、保持原大小写、每组不超过 50 个值，未传的字段为空数组或 `null`。

## 3. 错误响应

| HTTP | `error.code` | 触发场景 |
|---|---|---|
| 422 | `INVALID_QUERY` | 参数类型错误、空字符串、未知参数、超数量上限、`salary_min > salary_max`、对象数量不符合接口要求 |
| 404 | `NOT_FOUND` | 单对象接口的目标代码不存在（`/jobs/distance` 的职位不在基线候选集、`/regions/similar` 的地区未知） |
| 503 | `DATA_NOT_READY` | 数据或算法结果未加载 |
| 500 | `INTERNAL_ERROR` | 未预期异常 |

统一格式（不套第 2 节外壳）：

```json
{"error":{"code":"INVALID_QUERY","message":"salary_min 不能大于 salary_max","details":[{"field":"salary_min","reason":"out_of_range"}],"request_id":"req-3f9c1a2e"}}
```

- `details` 可为空数组；每项固定 `{field, reason}`。
- `request_id` 每次请求生成，同时写入服务日志。500 不在响应里返回堆栈、文件路径或 SQL。
- **后端必须覆盖框架默认的校验错误格式**，前端不需要兼容两套结构。
- 框架层的校验失败（FastAPI / Pydantic）也由同一处理器改写为上述格式，`reason` 取 `type`、`invalid`、`missing` 之一。

## 4. 筛选语义

普通统计接口（`/overview`、`/regions`、`/jobs/profile`、`/records`）支持 5 个重复查询参数：

| 参数 | 对应字段 | 说明 |
|---|---|---|
| `city` | `city` | 地区代码 |
| `job_title` | `job_title` | 职位类别代码 |
| `company_type` | `company_type` | 行业类别代码（**不是**企业规模或所有制） |
| `education` | `education` | 学历代码，无序类别 |
| `experience` | `experience` | 经验代码，无序类别 |
| `salary_min` | `salary_mid` | 闭区间下限，单位 K，有限非负 |
| `salary_max` | `salary_mid` | 闭区间上限，单位 K，有限非负 |

规则：

1. **同字段多值 OR，字段间 AND**。重复键表达多值：`/api/v1/overview?city=F047&city=P949&education=GI`。
2. 代码**精确匹配且区分大小写**，不做大小写归一、不做语义推断。
3. 未传某字段 = 不限制该字段。
4. 每个字段最多 **50** 个不同代码，超出 422；后端去重时保留首次出现顺序，不改大小写。
5. 传空字符串 → 422。**顶层未知参数一律拒绝**（防止把全局筛选误传给基线接口），不做静默忽略。
6. 筛选场景中**未知代码是合法的零结果**（200 + 计数 0 + 薪资 `null`），只有单对象接口的目标不存在才 404。
7. 启用任意薪资筛选时，只保留 `salary_status = valid_range` 且 `salary_unit = K` 的记录。未启用时，薪资无效记录**仍计入总量**。
8. 学历、经验只支持等值多选，不接受“本科及以上”“经验大于三年”这类顺序判断。
9. 响应 `meta.filters` 回填实际生效的条件；零记录时同样回填。

## 5. 枚举

| 枚举 | 取值 |
|---|---|
| `salary_status` | `valid_range`、`missing`、`unparsed`、`invalid_range`、`unsupported_unit`、`one_sided` |
| `salary_unit` | `"K"`、`"other"`、`null`（V1 主统计只接受 `K`） |
| `meta.scope` | `"filtered"`、`"global"` |

`valid_range` 且 `salary_unit = K` 时：`salary_lower`、`salary_upper`、`salary_mid` 均为有限数，两端都 > 0，下界 ≤ 上界，中点为两界均值。
其余状态下 `salary_mid` 一律 `null`，且不得用 `0` 或空串代替。

## 6. 接口清单

| 路径 | 作用域 | 参数 | `data` |
|---|---|---|---|
| `/api/v1/health` | — | 无 | 简短对象，无外壳 |
| `/api/v1/meta` | global | 无 | `fields, filter_options, capabilities, analysis_version, distance_candidates, sample_threshold` |
| `/api/v1/options/jobs` | global | `q, page, page_size` | `items, page, page_size, total` |
| `/api/v1/overview` | filtered | 通用筛选 | `total_records, company_count, job_count, salary_valid_count, salary_median` |
| `/api/v1/regions` | filtered | 通用筛选 | `items[RegionStats]` |
| `/api/v1/jobs/profile` | filtered | 通用筛选 + `job_title` 恰好 1 个 | `job_title, label, total_records, salary, distributions` |
| `/api/v1/records` | filtered | 通用筛选 + 分页 | `items[Record], page, page_size, total` |
| `/api/v1/jobs/distance` | global | `job_title` 重复 2～4 个 | `job_titles, matrix, components, method, analysis_version` |
| `/api/v1/regions/similar` | global | `city` 恰好 1 个，`limit` 1～10（默认 5） | `city, items, method, analysis_version` |

### 6.1 `GET /api/v1/health`

```json
{"status": "ok", "api_version": "1.0"}
```

数据库、算法结果均未加载时也必须 200，用于区分“进程活了”和“数据没好”。

### 6.2 `GET /api/v1/meta`

无参数；传任何参数都 422。

| 字段 | 类型 | 说明 |
|---|---|---|
| `fields` | array | 字段说明列表，每项 `{name, data_type, nullable, unit, description}` |
| `filter_options.city` | array | `{value, label}`，全量地区代码 |
| `filter_options.company_type` | array | `{value, label}`，全量行业代码 |
| `filter_options.education` | array | `{value, label}` |
| `filter_options.experience` | array | `{value, label}` |
| `capabilities` | object | 固定 `{real_names:false, geo:false, time_series:false, skills:false}` |
| `analysis_version` | string \| null | 算法未加载时为 `null` |
| `distance_candidates` | array \| null | 可参与距离计算的职位 `{value,label}`；算法未加载时为 `null` |
| `sample_threshold` | integer | 固定 `30`：有效薪资样本低于该值的对象不进主排名，仅作展示提示 |

**不返回职位全列表**（169,540 条），职位通过 `/options/jobs` 分页搜索。
`label` 只是稳定短标签，原代码在 `value`；标签不得被解释为真实名称。

### 6.3 `GET /api/v1/options/jobs`

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `q` | string | 无 | 对**原代码**做字面子串匹配，区分大小写，不做拼音或模糊匹配 |
| `page` | integer ≥1 | 1 | |
| `page_size` | integer 1～100 | 20 | |

```json
{"items":[{"job_title":"J001","label":"J001","total_records":420}],"page":1,"page_size":20,"total":5}
```

`total_records` 是该职位在当前数据版本下的记录数，不受页面筛选影响（global）。

### 6.4 `GET /api/v1/overview`

通用筛选。零记录时三项计数为 `0`，`salary_median` 为 `null`。

```json
{"total_records":1015,"company_count":288,"job_count":5,"salary_valid_count":742,"salary_median":7.5}
```

`salary_valid_count` 只统计 `valid_range` + `K`；`company_count` 是去重后的企业数，不等于各地区企业数之和。

### 6.5 `GET /api/v1/regions`

通用筛选，不分页（最多 371 行）。排序固定：`total_records` 降序，同数按 `city` 字典序。低频地区不静默丢弃。

`RegionStats`：

| 字段 | 类型 | 说明 |
|---|---|---|
| `city` | string | 地区代码 |
| `total_records` | integer | 发布记录数（分母，不因薪资无效而减少） |
| `company_count` | integer | 该地区去重企业数 |
| `salary_valid_count` | integer | 有效薪资记录数 |
| `salary` | object \| null | `{q1, median, q3, min, max}`；无有效薪资时整体 `null` |
| `small_sample` | boolean | `salary_valid_count < 30` |

```json
{"city":"F047","total_records":400,"company_count":120,"salary_valid_count":360,
 "salary":{"q1":5.0,"median":7.5,"q3":10.0,"min":2.0,"max":30.0},"small_sample":false}
```

`salary` 是**五数概括**（min / Q1 / median / Q3 / max），不是 1.5IQR 异常值箱线图。前端不得标成 Tukey 箱线图。

### 6.6 `GET /api/v1/jobs/profile`

通用筛选 + `job_title` **恰好 1 个**（0 个或多个 → 422）。目标职位存在但其他条件无结果时，返回正常空画像（200）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `job_title` | string | 回显代码 |
| `label` | string | 稳定短标签 |
| `total_records` | integer | 当前条件下记录数 |
| `salary` | object \| null | `{valid_count, q1, median, q3, min, max}`；`valid_count = 0` 时其余为 `null` |
| `distributions` | object | 固定四个键：`city`、`company_type`、`education`、`experience` |

每个 distribution 为：

```json
{"denominator":420,"items":[{"value":"GI","count":210,"share":0.5},{"value":null,"count":21,"share":0.05}]}
```

- 分母固定为 `total_records`，**未知类别也计入分母**，表示为 `value: null`。
- 返回**完整类别列表**，服务端不截断 Top-N。前端若归并为“其他”，必须显示合计，不能让人误以为总占比 100%。
- 零分母时 `denominator = 0`、`items = []`。

### 6.7 `GET /api/v1/records`

通用筛选 + 分页。排序固定 `source_row` 升序；`total` 是过滤后全部记录数，不是当前页条数。

`Record` 按数据契约 `3.2` 全字段返回：

`record_id`、`source_row`、`job_title`、`city`、`experience`、`education`、`company`、`company_type`、`salary_raw`、`salary_lower`、`salary_upper`、`salary_mid`、`salary_unit`、`pay_months`、`salary_status`、`is_extra_duplicate`

```json
{"record_id":"a1b2c3d4e5f6:second_data:2","source_row":2,"job_title":"J001","city":"F047",
 "experience":"EX1","education":"GI","company":"C001","company_type":"I01",
 "salary_raw":"5-6K","salary_lower":5.0,"salary_upper":6.0,"salary_mid":5.5,
 "salary_unit":"K","pay_months":null,"salary_status":"valid_range","is_extra_duplicate":false}
```

`salary_raw` 是原始文本，不被派生字段覆盖；页面显示的薪资单位取自本接口的 `salary_unit`，前端不自行换算后仍标 `K`。

### 6.8 `GET /api/v1/jobs/distance`

`job_title` 重复 **2～4** 个，不接受任何通用筛选参数（传了就 422）。全局基线，不随页面筛选重算。

| 字段 | 类型 | 说明 |
|---|---|---|
| `job_titles` | array | 按请求规范化后的顺序回显 |
| `matrix` | array | n×n，与 `job_titles` 同序；对称，对角线为 0；维度不可用时该项为 `null` |
| `components` | array | 只返回 i<j 的无序对 |
| `method` | object | `{name, version, dimensions, weights, salary_reference, reference_scope, min_salary_samples}` |
| `analysis_version` | string | 对应 `analysis_manifest.json` |

`components` 每项：

```json
{"left":"J001","right":"J002","industry":0.5,"region":0.35,"education":0.45,"experience":0.4,"salary":0.4,"total":0.42}
```

`total` 是各维等权平均。请求的职位不在 `/meta` 的 `distance_candidates` 内 → 404 `NOT_FOUND`；薪资参考范围为 0 → 503 `DATA_NOT_READY` 并说明，**不允许除零或临时改公式**。

### 6.9 `GET /api/v1/regions/similar`

`city` **恰好 1 个**；`limit` 1～10，默认 5。全局基线，不接受通用筛选。

| 字段 | 类型 | 说明 |
|---|---|---|
| `city` | string | 回显目标地区 |
| `items` | array | `{city, similarity, total_records}`，`similarity` 降序，同分按 `city` 升序，**不含自己** |
| `method` | string | 固定说明：`1 - TV(P‖Q)`，基于全局行业发布结构，不含薪资项，不随筛选重算 |
| `analysis_version` | string | |

已知地区但无可比较分布 → `items` 为空数组（200）。目标地区不存在 → 404。

## 7. 分页、排序与精度

- `page ≥ 1`，`page_size` 为 1～100。超出范围 → 422。
- 超过最后一页 → 200 + 空 `items` + 原 `total`，不报错。
- 分页接口的 `total` 恒为过滤后总数。
- 统计保留完整精度，**只在展示层舍入**；舍入值不回流参与计算。
- 分位数固定线性插值，与 `pandas.quantile(interpolation='linear')` 对齐。
- JSON 中不允许 `NaN` / `Infinity`，不可用数值一律 `null`。

## 8. 作用域：哪些随筛选变，哪些不变

| 接口 | 作用域 | 是否随页面筛选重算 |
|---|---|---|
| `/overview`、`/regions`、`/jobs/profile`、`/records` | `filtered` | 是 |
| `/meta`、`/options/jobs`、`/jobs/distance`、`/regions/similar` | `global` | 否，固定全局基线 |

`global` 接口的 `meta.filters` 为 `null`，`meta.scope` 为 `global`。前端必须在距离面板与相似地区面板显著标注“全局基线”，避免用户以为它跟着筛选变了。
把通用筛选传给 `global` 接口会得到 422 —— 这是刻意设计，不是缺陷。

## 9. 模拟数据与切换

- 共享样例在 `contracts/v1/examples/`，`data_version` 一律 `mock-v1`。
- 后端以 `APP_ALLOW_MOCK=1`（开发默认）启动时，无数据库也可返回样例，`data_version` 回 `mock-v1`，`/meta` 的 `analysis_version` 为 `mock-v1`。
- **答辩与最终验收必须 `APP_ALLOW_MOCK=0`**，否则真实数据缺失会被静默掩盖。
- 前端 `VITE_API_MODE=mock|real` 仍按协作契约 6.2 执行；real 模式失败直接报错，**不得回落到模拟数据**。
- 样例只保证结构与状态机正确，不保证任意筛选组合的语义正确性（协作契约 6.2 允许）。

## 10. 与前端现状的差异（C 必须修改，B 不提供兼容层）

当前 `frontend/src/api/types.ts`、`endpoints.ts` 是按“待确认假设”写的，与本契约有结构性差异：

| 项 | 本契约（权威） | 前端现状 | 处理 |
|---|---|---|---|
| 参数名 | `city`、`job_title`、`company_type` | `region`、`job`、`industry` | 改 `endpoints.ts` 的 `filterParams` |
| 响应结构 | 外壳包裹，数据在 `response.data` | 直接当扁平对象用 | `client.ts` 拆壳 |
| 命名风格 | `snake_case` | `camelCase` | 改 `types.ts` 全量字段名 |
| 多值参数 | 重复键 `?city=A&city=B` | 重复键（已一致） | 无需改 |
| `/records` 的 `salary_status` | 6 个取值 | `ok`/`invalid`/`unparsed` | 改 `types.ts` 与展示映射 |
| `/jobs/distance` | `job_titles` + `matrix` + `components[]` | `jobs`、`labels`、`components` 为字典 | 改组件取值 |
| `/regions` 的 `salary` | 五数概括 `q1/median/q3/min/max` | 含 `p05/p25/p50/p75/p95/sampleCount` | 收敛为五数概括 |
| `/jobs/profile` 的 `distributions` | 四个维度（含 `city`） | 三个维度 | 补 `city` |
| `/regions/similar` | `items[].city` | `items[].region` | 改字段名 |
| `/regions` 的 `industryShare` | **不提供**（见 CC-001） | 期望可选字段 | 缺失时显示“接口未提供” |

`label` 一律是短标签，原代码在 `value` / `city` / `job_title`，界面传参必须用原代码。

## 11. 对前端三个待确认问题的答复

C 在 `docs/design/request_contract_notes.md` 提的三个问题，答复如下：

**（1）多值参数是重复键还是逗号分隔？**
重复键。`?city=F047&city=P949`。保持顺序，不拼接分隔符。逗号分隔不支持。

**（2）`/regions` 是否提供 `industryShare` 与 `salary`？**
- `salary`：提供，但只有五数概括 `{q1, median, q3, min, max}`，不含 `p05/p95`，也不含 `sampleCount`（样本数在 `salary_valid_count`）。理由：协作契约 5.1 明确箱线图 V1 画五数概括。
- `industryShare`：**V1 不提供**。协作契约 5.1 的 `RegionStats` 没有该字段，而全量返回 371 地区 × 158 行业会产生数万条记录。这是契约缺口，需要三人拍板，见 CC-001。在确认前，比较区按“接口未提供”降级，不要用全量数据自行反推。

**（3）`/records` 的 `pageSize` 上限与排序？**
上限 100，默认 20；固定 `source_row` 升序；越界页返回空 `items` + 原 `total`。

## 12. 待决事项

### CC-001（需三人确认）`/regions` 的地区行业结构

C03 的“2～4 个地区比较行业占比”需要每个地区的行业分布。当前契约没有该字段，而全量返回不可行。

两个候选方案：

- **A（推荐）** 新增可选字段 `top_industries: [{value, count, share}] | null`，只返回前 5 个行业 + 一个 `value: null` 的“其他”合计项。响应约 371 × 6 ≈ 2200 条，约 150KB。
- **B** 新增 `GET /api/v1/regions/compare?city=..&city=..`，只在选中 2～4 个地区时返回完整行业向量。请求数更少、体积更小，但多一个接口。

未确认前 V1 保持现状，C 的比较区降级为计数对比。

### CC-002（通知级，已实现）小规模可选字段

以下字段是协作契约未列、但不影响既有字段语义的补充，已按第 0 节第 4 条通知：

- `/meta` 的 `sample_threshold`：把“有效薪资 < 30 不进主排名”的阈值显式返回，避免前端硬编码。
- `/meta` 的 `distance_candidates`：协作契约 5.4 已要求，此处明确类型。
- `/jobs/profile` 的 `label`：短标签，便于界面显示。

## 13. 变更记录

| 日期 | 版本 | 内容 | 影响 |
|---|---|---|---|
| 2026-11-22 | 1.0 | 首次冻结：9 个接口、外壳、错误、筛选、枚举、模拟样例 | A 确认单位与字段；C 按第 10 节改类型层 |
