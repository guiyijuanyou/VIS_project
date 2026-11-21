# UI 视觉规范落地说明（v2 重构）

负责人：人员三（C）。本文件记录设计规范的落地位置与取舍，代码为准，文档同步维护。

## 1. Design Tokens（唯一来源）

`frontend/src/styles/tokens.css`：色彩、字体、字号、间距、边框、圆角、尺寸、断点、过渡。
`frontend/src/styles/main.css`：全局基础样式与原子类（面板 `.panel`、按钮 `.btn/.btn--primary/.btn--ghost`、表单 `.field`、提示条 `.notice`、数字 `.num`、`.mono`、`.chart-note`、`.section-label`）。

图表无法解析 CSS 变量，故在 `frontend/src/charts/theme.ts` 登记同值常量：
`BRAND #294c69`、`BRAND_ACCENT #c45b52`、`WARNING_POINT #c28a3c`、`AXIS_COLOR #929ba6`、`GRID_COLOR #e2e6ea`，以及低饱和分类色板 `PALETTE`（同一类别全站同色）。

| 规范项 | 取值 |
|---|---|
| 页面背景 / 主内容 | `#f5f6f7` / `#ffffff` |
| 主文字 / 次级 / 弱化 | `#202a35` / `#697586` / `#929ba6` |
| 主品牌 / 深色强调 | `#294c69` / `#1d354a` |
| 边框 / 次级背景 | `#e2e6ea` / `#eef1f4` |
| 正向 / 负向 / 警示 | `#27836a` / `#c45b52` / `#c28a3c` |
| 圆角 | 4 / 6 / 8px（无胶囊） |
| 阴影 | 仅 `--shadow-overlay`，用于 Tooltip 与下拉，面板一律用边框 |
| 字体 | Inter → Microsoft YaHei → Noto Sans SC → PingFang SC → Arial |

## 2. 组件清单与落地位置

| 组件 | 文件 | 要点 |
|---|---|---|
| Sidebar | `components/Sidebar.vue` | 深色中性底、分组导航、内联线性 SVG 图标、底部数据版本与来源 |
| Topbar | `components/Topbar.vue` | 模块位置、条件摘要、清除筛选 |
| PageHeader | `components/PageHeader.vue` | 页面标题 + 统计口径副标题 + 右侧操作槽 |
| FilterPanel | `components/FilterPanel.vue` | 右侧常驻分析条件；长列表用 Select 追加，已选值用可移除 Tag |
| MetricCard | `components/MetricCard.vue` | 指标名/数值/单位/口径四级信息，不使用彩色大字与渐变 |
| ChartContainer | `components/ChartContainer.vue` | 统一标题、口径说明、右上元信息与内容留白 |
| DataTable | `components/DataTable.vue` + `table-types.ts` | 表头吸顶、行高统一、数值列右对齐与等宽数字、悬停高亮、列宽不足横向滚动 |
| Pagination | `components/Pagination.vue` | 总条数/每页/页码 + 上/下一页两级按钮 |
| SearchInput | `components/SearchInput.vue` | 受控输入 + 提交按钮 |
| Select | `components/Select.vue` | 原生 select 外观统一，一次性选择后复位 |
| Tabs | `components/Tabs.vue` | 下划线式页内切换（职位画像三维度） |
| Tag | `components/Tag.vue` | 4px 圆角，非胶囊；状态色区分 normal/brand/positive/negative/warning |
| Tooltip | `components/Tooltip.vue` | 补充原代码与口径，淡入、浅阴影（唯一允许的阴影使用场景之一） |
| EmptyState / LoadingState / ErrorState | `components/{Empty,Loading,Error}State.vue` | 三态独立；StateBlock 组合三者，保持原有 `:status/:error/:empty` 接口 |
| 图表组件 | `RegionScatter` / `RegionCompare` / `SimilarRegions` / `JobProfile` / `SalaryBox` / `DistanceMatrix` / `RecordTable` / `OverviewCards` | 全部改用 Token 与上述组件，内部不再自建配色与圆角 |

## 3. 冲突项 → 文件 → 处理方式

| # | 原样式冲突 | 文件 | 处理 |
|---|---|---|---|
| 1 | 调色板与规范不一致（冷蓝 #3b6dd8、卡片阴影、10px 圆角） | `styles/tokens.css`、`styles/main.css` | 全量替换为规范色板；圆角 4/6/8；卡片改用边框 |
| 2 | 胶囊形态筛选按钮（`border-radius: 999px`） | `styles/main.css`、`FilterPanel.vue`、`SimilarRegions.vue` | 改为 4px 圆角 Tag；长列表改为下拉追加 |
| 3 | 卡片投影 `--shadow-card` 用于所有面板（悬浮卡片感） | `styles/tokens.css`、各组件 | 删除，改用 1px 边框；阴影仅留给浮层 |
| 4 | 页头/页签/筛选/页脚挤在无层级的一列，无侧栏导航 | `App.vue` | 改为 Sidebar + Topbar + PageHeader + 主内容 + 右侧分析条件栏 |
| 5 | 每个页面各自排版图表卡（标题/说明样式重复且不一致） | 三个 `views/*.vue` | 统一使用 ChartContainer |
| 6 | 表格无统一规格：部分列未右对齐、行高与表头各异、无横向滚动导致内容被裁 | `RecordTable.vue`、`RegionCompare.vue`、`DistanceMatrix.vue` | 统一 DataTable；数值列右对齐 + tabular-nums；列宽不足改为横向滚动 |
| 7 | 指标卡无统计口径、单位混在数值里 | `OverviewCards.vue`、`JobProfile.vue` | 改用 MetricCard，口径与单位进入次级层级 |
| 8 | 状态展示原来集中在一个 StateBlock（加载/错误/空三种视觉混在一起） | `StateBlock.vue` | 拆为 LoadingState / EmptyState / ErrorState，StateBlock 组合，接口不变 |
| 9 | 图表色板含高饱和蓝与黄色，且坐标轴/图例样式各组件各写一套 | `charts/theme.ts` 及各图表 | 统一低饱和分类色板 + 坐标轴/图例/提示框默认样式 |
| 10 | 散点选中态用红色描边（红=负向语义，易误读） | `RegionScatter.vue` | 选中改用深色强调 + 其余点降透明度，红色不承担“选中”语义 |
| 11 | 分页按钮与“共 N 条”分散在卡片角标 | `RecordTable.vue` | 统一 Pagination 组件 |

未发现：渐变、玻璃拟态、发光、3D 图表、装饰性动画、饼图/雷达图滥用。

## 4. 待补充（规范未给出具体取值）

- 间距基数取 4px（--space-1..8），断点取 1200 / 1024（--bp-lg / --bp-md）——工程默认值，团队可统一调整。
- 图标库未引入（不新增 UI 依赖），侧栏与状态图标使用内联线性 SVG（16px，stroke 1.3–1.4）。
- 规范示例中的“较上期 +8.6%”同比信息：当前数据与接口没有时间维度，指标卡不展示变化率（见第 5 节冲突点）。

## 5. 规范与本项目数据的冲突（以不破坏数据准确性为准）

1. **时间范围 / 数据更新时间**：数据集无时间字段，接口也不返回更新时刻。Topbar 与 PageHeader 因此只展示条件、数据版本与接口模式，不虚构时间范围；规范中的 DateRangePicker 不在本项目中落地。
2. **地图（地理信息/分级设色）**：地区是代码（R001…），官方数据无经纬度，规范明确禁止把代码猜成真实地区，故不做地图。
3. **同比/环比**：无时间维度，指标卡不展示变化率，避免用编造的趋势增强“高级感”。
4. **雷达图/饼图**：规范本身要求禁止滥用，本项目结构与分布均用条形/箱线表达。
