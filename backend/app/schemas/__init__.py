"""响应数据模型。字段名与 docs/api/contract.md 一一对应。"""

from .common import (
    CodeOption,
    Distribution,
    SalaryQuantiles,
    SalaryStatus,
    SalarySummary,
    SalaryUnit,
    ShareItem,
)
from .jobs import (
    DistanceComponent,
    DistanceMethod,
    JobDistanceData,
    JobOptionItem,
    JobOptionsData,
    JobProfileData,
    ProfileDistributions,
)
from .meta import Capabilities, FieldDoc, FilterOptions, MetaData
from .overview import OverviewData
from .records import Record, RecordsData
from .regions import RegionStats, RegionsData, SimilarRegionItem, SimilarRegionsData

__all__ = [
    "Capabilities",
    "CodeOption",
    "DistanceComponent",
    "DistanceMethod",
    "Distribution",
    "FieldDoc",
    "FilterOptions",
    "JobDistanceData",
    "JobOptionItem",
    "JobOptionsData",
    "JobProfileData",
    "MetaData",
    "OverviewData",
    "ProfileDistributions",
    "Record",
    "RecordsData",
    "RegionStats",
    "RegionsData",
    "SalaryQuantiles",
    "SalaryStatus",
    "SalarySummary",
    "SalaryUnit",
    "ShareItem",
    "SimilarRegionItem",
    "SimilarRegionsData",
]
