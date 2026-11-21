# 前端（人员三 C）

Vue 3 + TypeScript + ECharts + Pinia + Vite。当前默认 **mock 模式**：所有数值来自
`src/mock/` 的模拟数据（文件头标注 SIMULATED），**不是真实统计**。人员二冻结接口后切换 real。

## 运行

```powershell
Set-Location VIS_project\frontend
npm ci            # 或 npm install
npm run dev       # http://localhost:5173
npm run build     # 先 vue-tsc 类型检查，再打包到 dist/
```

## mock / real 切换

```powershell
Copy-Item .env.example .env.local
# VITE_API_MODE=mock  → 使用 src/mock（默认）
# VITE_API_MODE=real  → 请求 VITE_API_BASE（默认 /api/v1，开发期由 vite 代理到 :8000）
```

real 模式下接口失败只显示错误态，**不会回落到模拟数据**；页头同时显示“真实接口/模拟数据”与数据版本。

## 已实现（对应分工 C02～C05）

- 统一请求层（`src/api/client.ts`）：单一路径入口、重复键多值参数、AbortController 取消、错误体解析、mock/real 切换。
- 全站唯一筛选状态（`src/stores/filter.ts`）：同字段 OR、不同字段 AND；切页保留、重置清空。
- 三页签：地区总览、职位画像与差异、条件比较与证据。
- 八个核心组件 + 三态（加载/错误/空结果）：`FilterPanel`、`OverviewCards`、`RegionScatter`、`RegionCompare`、`SimilarRegions`、`JobProfile`、`SalaryBox`、`DistanceMatrix`、`RecordTable`。
- 过期请求丢弃、模拟数据标记、无有效薪资显示为状态而非 0。

## 未做（属于其他人或待联调）

- 统计口径（分位数、重复口径、距离/相似度公式）由人员一提供、人员二实现；前端只展示与解释。
- 真实接口联调（H3/H4）待人员二提供 `/api/v1` 契约与实现，见 `docs/design/request_contract_notes.md`。
- 用户试用与修改前后截图（C06）见 `docs/design/usability_notes.md`（当前为空模板）。
