"""エラーモデル定義."""

from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel, Field


class EStatErrorCode(IntEnum):
    """e-Statエラーコード."""

    SUCCESS = 0
    NO_DATA = 1
    AUTH_ERROR = 100
    MISSING_PARAM = 101
    INVALID_PARAM = 102
    DATA_NOT_FOUND = 300
    # クライアント側エラー（e-Stat APIから返されるものではない）
    NETWORK_ERROR = 900
    SERVER_ERROR = 901
    VALIDATION_ERROR = 902


class ApiResult(BaseModel):
    """APIレスポンスの結果部分."""

    status: int = Field(..., alias="STATUS")
    error_msg: str = Field(..., alias="ERROR_MSG")
    date: str = Field(..., alias="DATE")

    @property
    def is_success(self) -> bool:
        """成功レスポンスかどうか."""
        return self.status == 0

    @property
    def is_no_data(self) -> bool:
        """該当データなしレスポンスかどうか."""
        return self.status == 1


class EStatError(BaseModel):
    """e-Statエラー情報."""

    code: EStatErrorCode
    message: str
    parameter: str | None = None

    @classmethod
    def from_api_result(cls, result: ApiResult) -> EStatError | None:
        """APIレスポンスからエラーを生成.

        Args:
            result: APIレスポンスの結果部分

        Returns:
            成功（status == 0）の場合はNone、それ以外（該当データなしを含む）はEStatError
        """
        if result.is_success:
            return None
        return cls(
            code=EStatErrorCode(result.status),
            message=result.error_msg,
        )
