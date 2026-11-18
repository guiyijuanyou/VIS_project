"""Reproducible clean-v1 pipeline. Run from any working directory."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
import pandas as pd

FIELDS = ['job_title','city','salary','experience','education','company','company_type']
STATUS = ['valid_range','missing','unparsed','invalid_range','unsupported_unit','one_sided']

def parse_salary(value):
    result = dict(salary_lower=None,salary_upper=None,salary_mid=None,
                  salary_unit=None,pay_months=None,salary_status='unparsed')
    if value is None or not str(value).strip():
        result['salary_status']='missing'
        return result
    text = str(value).strip()
    suffix = re.search(r'[·•]\s*(\d+)薪$',text)
    if suffix:
        result['pay_months']=int(suffix[1])
        if result['pay_months'] <= 0:
            result['salary_status']='invalid_range'
            return result
        text=text[:suffix.start()].strip()
    match = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*[-~～]\s*(-?\d+(?:\.\d+)?)\s*[Kk]',text)
    if match:
        lo,hi=map(float,match.groups())
        result.update(salary_lower=lo,salary_upper=hi,salary_unit='K')
        if 0 < lo <= hi:
            result.update(salary_mid=(lo+hi)/2,salary_status='valid_range')
        else:
            result['salary_status']='invalid_range'
    elif re.search(r'元|万|/天|/时|/年|每天|每小时',text):
        result.update(salary_unit='other',salary_status='unsupported_unit')
    elif re.fullmatch(r'\d+(?:\.\d+)?[Kk](?:以上|以下|起)?',text):
        result.update(salary_unit='K',salary_status='one_sided')
    return result

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(root):
    source=root/'data/JobWanted.xlsx'
    out=root/'data/processed/clean-v1'
    docs=root/'docs/data'
    out.mkdir(parents=True,exist_ok=True)
    docs.mkdir(parents=True,exist_ok=True)
    sha=digest(source)
    raw=pd.read_excel(source,sheet_name='second_data',dtype=str,keep_default_na=False)
    if list(raw.columns)!=FIELDS:
        raise ValueError(f'Unexpected columns: {list(raw.columns)}')
    duplicates=raw.duplicated(keep='first')
    inventory={c:{'distinct':int(raw[c].nunique()),'blank':int(raw[c].str.strip().eq('').sum()),
                  'top10':raw[c].value_counts().head(10).to_dict()} for c in FIELDS}
    salary_map={v:parse_salary(v) for v in raw.salary.unique()}
    patterns=raw.salary.value_counts().rename_axis('salary_raw').reset_index(name='count')
    patterns['status']=patterns.salary_raw.map(lambda x:salary_map[x]['salary_status'])
    patterns.to_csv(out/'salary_patterns.csv',index=False,encoding='utf-8-sig')
    clean=raw.rename(columns={'salary':'salary_raw'}).copy()
    for c in FIELDS:
        if c!='salary':
            clean[c]=clean[c].str.strip().replace('',None)
    clean.insert(0,'source_row',range(2,len(clean)+2))
    clean.insert(0,'record_id',[f'{sha[:12]}:second_data:{i}' for i in clean.source_row])
    parsed=pd.DataFrame([salary_map[v] for v in raw.salary])
    clean=pd.concat([clean,parsed],axis=1)
    clean['pay_months']=pd.array(clean.pay_months,dtype='Int64')
    clean['is_extra_duplicate']=duplicates
    target=out/'jobs_clean.parquet'
    clean.to_parquet(target,index=False)
    quality={'raw_count':len(raw),'output_count':len(clean),'extra_duplicate_count':int(duplicates.sum()),
             'salary_status_counts':clean.salary_status.value_counts().to_dict(),
             'valid_salary_fraction':float(clean.salary_status.eq('valid_range').mean()),'columns':inventory}
    dump(out/'quality_report.json',quality)
    dump(out/'manifest.json',dict(data_version='clean-v1',schema_version='1.0',source_sha256=sha,
         output_sha256=digest(target),source_sheet='second_data',raw_count=len(raw),output_count=len(clean),
         extra_duplicate_count=int(duplicates.sum()),duplicate_policy='keep_all',
         salary_basis='quoted_range_midpoint',created_at=datetime.now(timezone.utc).isoformat()))
    sample=pd.concat([clean.groupby('salary_status',sort=True).head(3),clean.head(50)]).drop_duplicates('record_id').head(50)
    dump(out/'sample_records.json',json.loads(sample.to_json(orient='records',force_ascii=False)))
    city=clean.city.value_counts().index[0]
    edu=clean.education.value_counts().index[0]
    job=clean.job_title.value_counts().index[0]
    cases=[{}, {'city':[city]}, {'city':[city],'education':[edu]}, {'job_title':[job]}, {'city':['__not_a_city__']}]
    checks=[]
    for filters in cases:
        part=clean
        for k,v in filters.items():
            part=part[part[k].isin(v)]
        values=part.loc[part.salary_status.eq('valid_range') & part.salary_unit.eq('K'),'salary_mid'].dropna()
        checks.append({'filters':filters,'total_records':len(part),'company_count':int(part.company.nunique()),
                       'job_count':int(part.job_title.nunique()),'salary_valid_count':len(values),
                       'salary_median':float(values.median()) if len(values) else None,
                       'quantile_method':'linear'})
    dump(out/'reference_checks.json',checks)
    properties={c:{'type':['string','null']} for c in ['job_title','city','experience','education','company','company_type','salary_raw']}
    properties.update(record_id={'type':'string','minLength':1},source_row={'type':'integer','minimum':2},
        salary_unit={'enum':['K','other',None]},pay_months={'type':['integer','null'],'minimum':1},
        salary_status={'enum':STATUS},is_extra_duplicate={'type':'boolean'})
    for c in ['salary_lower','salary_upper','salary_mid']:
        properties[c]={'type':['number','null']}
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Clean record v1',
            'type':'object','additionalProperties':False,'required':list(properties),'properties':properties}
    dump(root/'contracts/v1/data.schema.json',schema)
    import jsonschema
    validator=jsonschema.Draft202012Validator(schema)
    for item in json.loads(sample.to_json(orient='records')):
        validator.validate(item)
    restored=pd.read_parquet(target)
    assert len(restored)==len(raw) and restored.record_id.is_unique
    assert restored.salary_mid.notna().equals(restored.salary_status.eq('valid_range'))
    lines=['# 数据质量报告','',f'原始记录：{len(raw):,}；输出：{len(clean):,}；保留全部记录。',
           f'完全重复额外记录：{int(duplicates.sum())}，只标记不删除。',f'来源 SHA-256：`{sha}`','',
           '## 薪资状态','', '| 状态 | 数量 |','|---|---:|']
    lines += [f'| {k} | {v} |' for k,v in quality['salary_status_counts'].items()]
    lines += ['', '## 边界与后续工作','',
              '- K 是报价单位，本轮不声称支付周期已获官方确认，不折算为实际月收入。',
              '- 非 K 单位、单边区间和未解析值不进入主薪资统计，原记录仍计入发布量。',
              '- 当前规则是保守第一版，需人工复核 salary_patterns.csv 的低频及未解析格式。',
              '- 没有自动推断真实城市、学历、经验或行业名称。',
              '- 已验证 Parquet 回读、记录 ID 唯一、样例 JSON Schema 和薪资状态一致性；未完成同伴验收。']
    (docs/'quality_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in quality.items() if k!='columns'},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    run(parser.parse_args().root)
