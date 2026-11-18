# 廖杰的数据工作交接：clean-v1

本轮完成第一版可复现的数据清洗与检查流程。尚未完成同伴 H1/H2 验收、100 条人工审核、画像/距离/相似算法与最终五题分析。

## 文件

- `scripts/clean_data.py`：从原始 Excel 生成标准数据和报告，默认根目录由脚本位置确定。
- `contracts/v1/data.schema.json`：记录 JSON Schema；数值与状态的语义约束另由脚本断言检查。
- `data/processed/clean-v1/jobs_clean.parquet`：全量记录，保留重复标记。
- 同目录 `sample_records.json`：50 条样例，优先覆盖不同解析状态。
- 同目录 `manifest.json`：源文件/输出校验值及版本。
- 同目录 `quality_report.json`、`salary_patterns.csv`：字段、薪资格式和频次。
- 同目录 `reference_checks.json`：5 组筛选条件及预期结果。
- `docs/data/quality_report.md`：本次运行的质量汇总。
- `tests/data/test_salary.py`：关键薪资边界测试。

## 本机以外如何复现

需要 Python 3.12 及 pandas、openpyxl、pyarrow、jsonschema。由周士博将兼容版本统一加入项目依赖；本次没有覆盖他负责的 requirements.txt。

```powershell
python scripts/clean_data.py
python -m unittest discover -s tests/data -p "test_*.py"
```

本次运行使用的具体版本见 `docs/data/runtime_versions.txt`，依赖安装进团队虚拟环境后不需要 Codex 的绝对解释器路径。

## 口径

默认保留全部记录，重复仅标记。主薪资指标只采用合法 K 区间的中点；其他单位不转换，不猜月薪或年薪。无后缀的发薪月数为 null。代码保持大小写，不推断真实名称。

`record_id` 来自源文件哈希前缀、工作表和行号；原始 salary 保存在 salary_raw。解析失败不删招聘记录，薪资中点为 null。

## 交给周士博

先读 schema 和样例，导入 Parquet，核对 manifest 行数，再用 reference_checks 对照五组结果。给出验收日志后才算 H1/H2 完成；本交付不代替你的确认。

## 交给陶嘉义

样例是数据行，不是 API 响应。按周士博的接口外壳封装后使用；展示 null、不同薪资状态、原代码与来源行号。不能直接把这份行样例当作统计接口。

## 廖杰下一步

1. 人工检查 salary_patterns.csv 的未解析、其他单位、单边与异常格式。
2. 按状态和格式抽检至少 100 条并记录人工判断；不能把自动断言通过当成人工审核。
3. 若修改解析规则，升级规则记录并重新生成全部产物与校验值。
4. 接着完成职位画像、差异度和地区相似度；这些不需要等前后端。

交付分支：feat/data-clean-v1。代码、文档、Schema 和小样交接文件纳入版本管理；全量 Parquet、薪资格式 CSV 和 IDE 文件留在本地，可运行脚本重新生成。
