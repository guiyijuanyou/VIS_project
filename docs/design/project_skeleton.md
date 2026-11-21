# 项目骨架与文件所有权（v1）

记录人：人员三（C）。本文件只描述骨架与占位，不代替各人的交付文档；
`README.md`、`requirements.txt`、`.gitignore` 的内容由人员二（B）汇总维护。

```text
VIS_project/
  README.md                 B（保留原文件，骨架未改）
  requirements.txt          B（占位，仅列出待锁定依赖名）
  .gitignore                B（骨架提供了前端/后端必需条目）
  data/                     原始三文件只读
  data/processed/           A（README 占位：清洗数据、画像输出）
  scripts/                  A（4 个脚本占位，均 NotImplementedError）
  config/cleaning_rules.json A（占位 JSON）
  tests/data/               A（README 占位）
  backend/app/              B（main.py + routers/* 占位，均 TODO）
  backend/scripts/import_data.py  B（占位）
  tests/api/                B（README 占位）
  docs/data|api|analysis|validation|meetings/  A/B 各自 README 占位
  docs/design/              C（草图、交互、契约假设、可用性）
  deliverables/             三人（README 占位）
  frontend/                 C（唯一已实现的可运行部分）
```

## 前端（C）结构

```text
frontend/
  package.json tsconfig.json vite.config.ts index.html .env.example
  src/main.ts App.vue                App = Sidebar + Topbar + 主内容 + 分析条件栏
  src/router/index.ts                三个页签（hash 路由，切页保留条件）
  src/api/{client,endpoints,types,error}.ts   统一请求层 + mock/real 切换
  src/mock/{dataset,handlers}.ts     模拟数据与模拟响应（文件头标注 SIMULATED）
  src/stores/filter.ts               全站唯一筛选状态
  src/composables/{useAsyncQuery,useECharts}.ts
  src/styles/{tokens,main}.css       Design Tokens + 全局原子类（唯一视觉来源）
  src/charts/theme.ts                图表色板与坐标轴/图例/提示框默认样式
  src/components/
    Sidebar Topbar PageHeader ChartContainer MetricCard
    FilterPanel DataTable(table-types.ts) Pagination SearchInput Select Tabs Tag Tooltip
    EmptyState LoadingState ErrorState StateBlock
    OverviewCards RegionScatter RegionCompare SimilarRegions
    JobProfile SalaryBox DistanceMatrix RecordTable
  src/views/                         三个页签视图（PageHeader + ChartContainer）
  src/utils/format.ts                计数/占比/薪资/状态的展示规则
```

视觉规范落地说明见 `ui_style_guide.md`。


## 边界声明

- 人员三只实现 `frontend/` 与 `docs/design/`；A/B 的目录只放占位。
- 前端不重算统计口径：分位数、重复口径、距离公式、相似度均由后端/人员一提供，界面只展示与解释。
