"""Unit tests for error models."""

from e_stat_mcp.models.errors import ApiResult, EStatError, EStatErrorCode


class TestEStatErrorCode:
    """EStatErrorCodeのテスト."""

    def test_success_code(self) -> None:
        """成功コードの値が正しいこと."""
        assert int(EStatErrorCode.SUCCESS) == 0

    def test_no_data_code(self) -> None:
        """該当データなしコードの値が正しいこと."""
        assert int(EStatErrorCode.NO_DATA) == 1

    def test_auth_error_code(self) -> None:
        """認証エラーコードの値が正しいこと."""
        assert int(EStatErrorCode.AUTH_ERROR) == 100

    def test_missing_param_code(self) -> None:
        """パラメータ未指定コードの値が正しいこと."""
        assert int(EStatErrorCode.MISSING_PARAM) == 101

    def test_invalid_param_code(self) -> None:
        """パラメータ不正コードの値が正しいこと."""
        assert int(EStatErrorCode.INVALID_PARAM) == 102

    def test_data_not_found_code(self) -> None:
        """データ不存在コードの値が正しいこと."""
        assert int(EStatErrorCode.DATA_NOT_FOUND) == 300


class TestEStatError:
    """EStatErrorモデルのテスト."""

    def test_create_error(self) -> None:
        """エラーを作成できること."""
        error = EStatError(
            code=EStatErrorCode.AUTH_ERROR,
            message="認証に失敗しました",
        )
        assert error.code == EStatErrorCode.AUTH_ERROR
        assert error.message == "認証に失敗しました"
        assert error.parameter is None

    def test_create_error_with_parameter(self) -> None:
        """パラメータを含むエラーを作成できること."""
        error = EStatError(
            code=EStatErrorCode.INVALID_PARAM,
            message="パラメータが不正です",
            parameter="statsDataId",
        )
        assert error.code == EStatErrorCode.INVALID_PARAM
        assert error.parameter == "statsDataId"

    def test_from_api_result_success(self) -> None:
        """成功レスポンスからはNoneを返すこと."""
        result = ApiResult.model_validate(
            {
                "STATUS": 0,
                "ERROR_MSG": "正常に終了しました",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            }
        )
        error = EStatError.from_api_result(result)
        assert error is None

    def test_from_api_result_auth_error(self) -> None:
        """認証エラーレスポンスからエラーを生成できること."""
        result = ApiResult.model_validate(
            {
                "STATUS": 100,
                "ERROR_MSG": "認証に失敗しました",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            }
        )
        error = EStatError.from_api_result(result)
        assert error is not None
        assert error.code == EStatErrorCode.AUTH_ERROR
        assert error.message == "認証に失敗しました"

    def test_from_api_result_no_data(self) -> None:
        """該当データなしレスポンスからエラーを生成できること."""
        result = ApiResult.model_validate(
            {
                "STATUS": 1,
                "ERROR_MSG": "該当するデータがありません",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            }
        )
        error = EStatError.from_api_result(result)
        assert error is not None
        assert error.code == EStatErrorCode.NO_DATA
