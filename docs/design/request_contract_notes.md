# 前端对接口的待确认假设（C03/C06）

负责人：人员三（C）。用途：说明前端**目前按什么形状**调用接口，便于人员二（B03）在
`docs/api/contract.md` 冻结时逐条确认或否决。这不是契约本身，契约以 B 的文档为准。

分工文件第 9 行提到的 `协作契约_V1.md` **当前不在仓库中**，因此以下内容全部标为“待确认”。

## 1. 路径与参数命名

- 基址：`/api/v1`（前端 `VITE_API_BASE`，开发期走 vite 代理到 `http://127.0.0.1:8000`）。
- 已用到的路径：`/meta`、`/options/jobs`、`/overview`、`/regions`、`/jobs/profile`、`/jobs/distance`、`/regions/similar`、`/records`。
- 多值参数：`region=R005&region=R018`（重复键）。若契约采用逗号分隔，只需改 `src/api/client.ts` 的 `buildSearchParams` 与 mock 的 `asArray`。
- 参数名：`region / industry / job / education / experience`（单数、精确匹配、区分大小写）；分页 `page`（从 1 起）、`pageSize`（明细默认 20，上限 100）；职位搜索 `q`。

## 2. 响应结构

逐字段定义见 `frontend/src/api/types.ts`（含注释）。需要注意的三处：

1. `/regions` 的每个地区除计数外，还需要
   - `industryShare: {code,label,count,share}[]`——C03 的“行业占比比较”必须有它；
   - `salary: {p05,p25,p50,p75,p95,min,max,sampleCount,unit} | null`——比较区的 P25～P75 与箱线。
   两者目前是**可选字段**：缺失时界面显示“接口未提供”，不会自己用全量数据反推。
2. `/jobs/distance` 返回矩阵 + `components["A|B"]` 分量数组 + `algorithmVersion` + `referenceSet` + `warnings`；
   前端不做任何距离计算，只做展示与解释。
3. `/regions/similar` 必须自带 `method` 与 `reference` 文案（例如“全局行业发布结构，不随筛选重算”），界面原样展示，避免被读成地理相似。

## 3. 错误与空结果

- 错误响应体假设为 `{ code, message, detail? }`，非 2xx 一律当作失败（`src/api/error.ts`）。
- 无结果返回空数组 + 计数 0（不是 404），前端显示空状态提示。
- 无有效薪资返回 `null`，禁止返回 0（分工第 10 节第 7 条）。

## 4. 前端侧的实现约束（供 B 验证联调时对照）

- 请求可取消：`AbortController`；过期响应按序号丢弃。
- 筛选条件是全站唯一来源，切换页签不重置。
- mock 模式在页头与响应 `meta.mock = true` 双重标注；real 失败不回落 mock。

## 5. 需要 B 明确回答的三件事

1. 多值参数是重复键还是逗号分隔？
2. `/regions` 是否提供 `industryShare` 与 `salary`（否则 C03/C05 的比较区只能显示计数）？
3. `/records` 的 `pageSize` 上限与排序规则（当前假设按 `source_row` 升序、上限 100）。
