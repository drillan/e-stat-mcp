"""Pydanticモデル定義."""

from e_stat_mcp.models.api import (
    ClassInfo,
    ClassItem,
    DatasetInfo,
    DatasetListResponse,
    DataValue,
    MetaInfoResponse,
    StatsDataResponse,
    StatsListResponse,
    StatsTable,
)
from e_stat_mcp.models.errors import ApiResult, EStatError, EStatErrorCode
from e_stat_mcp.models.tools import (
    ClassItemInfo,
    DatasetResult,
    GetDatasetDataRequest,
    GetMetaInfoRequest,
    GetStatsDataRequest,
    ListDatasetsRequest,
    MetaInfoResult,
    SearchStatsRequest,
    SearchStatsResult,
    StatsDataItem,
    StatsDataResult,
)

__all__ = [
    # API Response Models
    "ApiResult",
    "StatsTable",
    "StatsListResponse",
    "ClassItem",
    "ClassInfo",
    "MetaInfoResponse",
    "DataValue",
    "StatsDataResponse",
    "DatasetInfo",
    "DatasetListResponse",
    # Error Models
    "EStatErrorCode",
    "EStatError",
    # Tool Models
    "SearchStatsRequest",
    "SearchStatsResult",
    "GetStatsDataRequest",
    "StatsDataItem",
    "GetMetaInfoRequest",
    "ClassItemInfo",
    "MetaInfoResult",
    "ListDatasetsRequest",
    "DatasetResult",
    "GetDatasetDataRequest",
    "StatsDataResult",
]
