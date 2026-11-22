# contracts/v1（人员二 B 维护）

接口契约 v1 的**共享模拟响应**与验收用例，供三人独立开发用。配合 `docs/api/contract.md` 阅读。

```text
contracts/v1/
  examples/                # 14 个 mock-v1 响应，结构即真实响应
  acceptance_cases.json    # 12 条集成用例（H2 后填真实预期数）
  tools/gen_examples.py    # 确定性生成器，改字段后重跑即可
```

## 约定

- 所有样例 `data_version` 为 `mock-v1`，仅证明结构与状态机，不构成分析结论。
- 生成器不引入随机数：同一份脚本重跑，输出逐字节一致。
- 脚本内置一致性断言：份额和为 1、矩阵对称且对角为 0、相似列表不含自身、`valid_range` 记录中点等于两界均值。
- 字段名一律 `snake_case`，与 `docs/api/contract.md` 一致。

## 重新生成

```powershell
.\.venv\Scripts\python.exe contracts\v1\tools\gen_examples.py
```

改契约字段时，先改 `docs/api/contract.md`，再改生成器，最后重跑并提交输出。

## 样例用途

| 文件 | 用途 |
|---|---|
| `meta.json` | 选项、字段说明、能力开关 |
| `options.jobs.json` | 职位搜索分页 |
| `overview.normal.json` / `overview.empty.json` | 正常 / 零结果 |
| `regions.normal.json` / `regions.no_salary.json` | 正常 / 无有效薪资与样本不足 |
| `profile.normal.json` / `profile.empty.json` | 正常画像 / 空画像 |
| `records.page1.json` / `records.last_page.json` | 首页 / 末页（15 条） |
| `distance.normal.json` | 3 职位差异矩阵与分量 |
| `similar.normal.json` | 相似地区列表 |
| `error.validation.json` / `error.not_ready.json` | 422 / 503 错误体 |
