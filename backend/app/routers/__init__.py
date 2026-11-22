"""路由注册表。路径前缀 /api/v1 由 main.py 统一挂载。"""

from . import health, jobs, meta, options, overview, records, regions

__all__ = ["health", "jobs", "meta", "options", "overview", "records", "regions"]
