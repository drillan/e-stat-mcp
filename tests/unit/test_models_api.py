"""Unit tests for API response models."""

import pytest
from pydantic import ValidationError

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
from e_stat_mcp.models.errors import ApiResult


class TestApiResult:
    """ApiResultモデルのテスト."""

    def test_valid_success_result(self) -> None:
        """正常終了のレスポンスをパースできること."""
        data = {
            "STATUS": 0,
            "ERROR_MSG": "正常に終了しました",
            "DATE": "2026-01-07T12:00:00.000+09:00",
        }
        result = ApiResult.model_validate(data)
        assert result.status == 0
        assert result.error_msg == "正常に終了しました"
        assert result.is_success is True
        assert result.is_no_data is False

    def test_no_data_result(self) -> None:
        """該当データなしのレスポンスをパースできること."""
        data = {
            "STATUS": 1,
            "ERROR_MSG": "該当するデータがありません",
            "DATE": "2026-01-07T12:00:00.000+09:00",
        }
        result = ApiResult.model_validate(data)
        assert result.status == 1
        assert result.is_success is False
        assert result.is_no_data is True

    def test_error_result(self) -> None:
        """エラーレスポンスをパースできること."""
        data = {
            "STATUS": 100,
            "ERROR_MSG": "認証に失敗しました",
            "DATE": "2026-01-07T12:00:00.000+09:00",
        }
        result = ApiResult.model_validate(data)
        assert result.status == 100
        assert result.is_success is False
        assert result.is_no_data is False

    def test_missing_required_field(self) -> None:
        """必須フィールドがない場合エラーになること."""
        data = {
            "STATUS": 0,
            "DATE": "2026-01-07T12:00:00.000+09:00",
        }
        with pytest.raises(ValidationError):
            ApiResult.model_validate(data)


class TestStatsTable:
    """StatsTableモデルのテスト."""

    def test_valid_stats_table(self) -> None:
        """統計表情報をパースできること."""
        data = {
            "@id": "0003348423",
            "STAT_NAME": "国勢調査",
            "GOV_ORG": "総務省",
            "TITLE": "人口等基本集計（男女・年齢・配偶関係，世帯の構成，住居の状態など）",
        }
        table = StatsTable.model_validate(data)
        assert table.id == "0003348423"
        assert table.stat_name == "国勢調査"
        assert table.gov_org == "総務省"
        assert table.title.startswith("人口等基本集計")

    def test_stats_table_with_optional_fields(self) -> None:
        """オプションフィールドを含む統計表情報をパースできること."""
        data = {
            "@id": "0003348423",
            "STAT_NAME": "国勢調査",
            "GOV_ORG": "総務省",
            "TITLE": "人口等基本集計",
            "CYCLE": "5年",
            "SURVEY_DATE": "202010",
            "OPEN_DATE": "2021-06-25",
            "SMALL_AREA": 0,
            "MAIN_CATEGORY": "人口・世帯",
            "SUB_CATEGORY": "人口",
        }
        table = StatsTable.model_validate(data)
        assert table.cycle == "5年"
        assert table.survey_date == "202010"
        assert table.open_date == "2021-06-25"
        assert table.small_area == 0
        assert table.main_category == "人口・世帯"
        assert table.sub_category == "人口"


class TestStatsListResponse:
    """StatsListResponseモデルのテスト."""

    def test_valid_response_with_tables(self) -> None:
        """統計表リストを含むレスポンスをパースできること."""
        data = {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "正常に終了しました",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            },
            "PARAMETER": {"LANG": "J"},
            "DATALIST_INF": {
                "NUMBER": 2,
                "TABLE_INF": [
                    {
                        "@id": "0003348423",
                        "STAT_NAME": "国勢調査",
                        "GOV_ORG": "総務省",
                        "TITLE": "人口等基本集計",
                    },
                    {
                        "@id": "0003348424",
                        "STAT_NAME": "国勢調査",
                        "GOV_ORG": "総務省",
                        "TITLE": "就業状態等基本集計",
                    },
                ],
            },
        }
        response = StatsListResponse.model_validate(data)
        assert response.result.is_success
        tables = response.get_tables()
        assert len(tables) == 2
        assert tables[0].id == "0003348423"
        assert tables[1].id == "0003348424"

    def test_response_with_single_table(self) -> None:
        """単一の統計表を含むレスポンスをパースできること（配列でなくオブジェクト）."""
        data = {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "正常に終了しました",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            },
            "PARAMETER": {"LANG": "J"},
            "DATALIST_INF": {
                "NUMBER": 1,
                "TABLE_INF": {
                    "@id": "0003348423",
                    "STAT_NAME": "国勢調査",
                    "GOV_ORG": "総務省",
                    "TITLE": "人口等基本集計",
                },
            },
        }
        response = StatsListResponse.model_validate(data)
        tables = response.get_tables()
        assert len(tables) == 1
        assert tables[0].id == "0003348423"

    def test_empty_response(self) -> None:
        """該当データなしのレスポンスを処理できること."""
        data = {
            "RESULT": {
                "STATUS": 1,
                "ERROR_MSG": "該当するデータがありません",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            },
            "PARAMETER": {"LANG": "J"},
        }
        response = StatsListResponse.model_validate(data)
        assert response.result.is_no_data
        tables = response.get_tables()
        assert len(tables) == 0


class TestClassItem:
    """ClassItemモデルのテスト."""

    def test_valid_class_item(self) -> None:
        """分類項目をパースできること."""
        data = {
            "@code": "001",
            "$": "総数",
            "@level": "1",
        }
        item = ClassItem.model_validate(data)
        assert item.code == "001"
        assert item.name == "総数"
        assert item.level == "1"

    def test_class_item_with_unit(self) -> None:
        """単位を含む分類項目をパースできること."""
        data = {
            "@code": "T001",
            "$": "人口",
            "@unit": "人",
        }
        item = ClassItem.model_validate(data)
        assert item.code == "T001"
        assert item.name == "人口"
        assert item.unit == "人"

    def test_class_item_with_parent_code(self) -> None:
        """親コードを含む分類項目をパースできること."""
        data = {
            "@code": "002",
            "$": "男",
            "@level": "2",
            "@parentCode": "001",
        }
        item = ClassItem.model_validate(data)
        assert item.code == "002"
        assert item.parent_code == "001"

    def test_class_item_with_at_name_format(self) -> None:
        """@name形式の分類項目をパースできること."""
        data = {
            "@code": "T001",
            "@name": "人口",
            "@level": "1",
        }
        item = ClassItem.model_validate(data)
        assert item.code == "T001"
        assert item.name == "人口"
        assert item.level == "1"

    def test_class_item_missing_name_field_raises_error(self) -> None:
        """名称フィールドがない場合にエラーになること."""
        data = {
            "@code": "001",
            "@level": "1",
        }
        with pytest.raises(ValidationError) as exc_info:
            ClassItem.model_validate(data)
        assert "ClassItemに名称フィールドがありません" in str(exc_info.value)


class TestClassInfo:
    """ClassInfoモデルのテスト."""

    def test_valid_class_info(self) -> None:
        """分類情報をパースできること."""
        data = {
            "@id": "tab",
            "@name": "表章項目",
            "CLASS": [
                {"@code": "T001", "$": "人口"},
                {"@code": "T002", "$": "世帯数"},
            ],
        }
        info = ClassInfo.model_validate(data)
        assert info.id == "tab"
        assert info.name == "表章項目"
        assert len(info.items) == 2
        assert info.items[0].code == "T001"

    def test_class_info_with_single_item(self) -> None:
        """単一の分類項目（辞書）を含む場合をパースできること."""
        data = {
            "@id": "tab",
            "@name": "表章項目",
            "CLASS": {"@code": "T001", "$": "人口"},
        }
        info = ClassInfo.model_validate(data)
        assert info.id == "tab"
        assert info.name == "表章項目"
        assert len(info.items) == 1
        assert info.items[0].code == "T001"
        assert info.items[0].name == "人口"

    def test_class_info_with_none_class(self) -> None:
        """CLASSがNoneの場合に空リストになること."""
        data = {
            "@id": "tab",
            "@name": "表章項目",
            "CLASS": None,
        }
        info = ClassInfo.model_validate(data)
        assert info.id == "tab"
        assert info.items == []

    def test_class_info_without_class_field(self) -> None:
        """CLASSフィールドがない場合に空リストになること."""
        data = {
            "@id": "tab",
            "@name": "表章項目",
        }
        info = ClassInfo.model_validate(data)
        assert info.id == "tab"
        assert info.items == []

    def test_class_info_with_invalid_class_type_raises_error(self) -> None:
        """CLASSに予期しない型が渡された場合にエラーになること."""
        data = {
            "@id": "tab",
            "@name": "表章項目",
            "CLASS": "invalid_string",
        }
        with pytest.raises(ValidationError) as exc_info:
            ClassInfo.model_validate(data)
        assert "CLASSフィールドに予期しない型が渡されました" in str(exc_info.value)


class TestMetaInfoResponse:
    """MetaInfoResponseモデルのテスト."""

    def test_valid_meta_info_response(self) -> None:
        """メタ情報レスポンスをパースできること."""
        data = {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "正常に終了しました",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            },
            "PARAMETER": {"LANG": "J"},
            "CLASS_INF": {
                "CLASS_OBJ": [
                    {
                        "@id": "tab",
                        "@name": "表章項目",
                        "CLASS": [
                            {"@code": "T001", "$": "人口"},
                        ],
                    },
                    {
                        "@id": "cat01",
                        "@name": "性別",
                        "CLASS": [
                            {"@code": "001", "$": "総数"},
                            {"@code": "002", "$": "男"},
                            {"@code": "003", "$": "女"},
                        ],
                    },
                ],
            },
        }
        response = MetaInfoResponse.model_validate(data)
        assert response.result.is_success
        class_objects = response.get_class_objects()
        assert len(class_objects) == 2
        assert class_objects[0].id == "tab"
        assert class_objects[1].id == "cat01"
        assert len(class_objects[1].items) == 3


class TestDataValue:
    """DataValueモデルのテスト."""

    def test_valid_data_value(self) -> None:
        """統計データ値をパースできること."""
        data = {
            "@tab": "T001",
            "@cat01": "001",
            "@area": "00000",
            "@time": "2020000000",
            "$": "126146099",
            "@unit": "人",
        }
        value = DataValue.model_validate(data)
        assert value.tab == "T001"
        assert value.cat01 == "001"
        assert value.area == "00000"
        assert value.time == "2020000000"
        assert value.value == "126146099"
        assert value.unit == "人"
        assert value.numeric_value == 126146099.0

    def test_data_value_with_comma(self) -> None:
        """カンマ区切りの数値をパースできること."""
        data = {
            "@tab": "T001",
            "$": "1,234,567",
        }
        value = DataValue.model_validate(data)
        assert value.numeric_value == 1234567.0

    def test_data_value_with_missing_value(self) -> None:
        """欠損値を処理できること."""
        test_cases = ["-", "...", "x", "*", "…"]
        for missing in test_cases:
            data = {
                "@tab": "T001",
                "$": missing,
            }
            value = DataValue.model_validate(data)
            assert value.numeric_value is None

    def test_data_value_with_invalid_number(self) -> None:
        """変換できない値を処理できること."""
        data = {
            "@tab": "T001",
            "$": "N/A",
        }
        value = DataValue.model_validate(data)
        assert value.numeric_value is None


class TestStatsDataResponse:
    """StatsDataResponseモデルのテスト."""

    def test_valid_stats_data_response(self) -> None:
        """統計データレスポンスをパースできること."""
        data = {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "正常に終了しました",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            },
            "PARAMETER": {"LANG": "J"},
            "STATISTICAL_DATA": {
                "CLASS_INF": {
                    "CLASS_OBJ": [
                        {
                            "@id": "tab",
                            "@name": "表章項目",
                            "CLASS": [{"@code": "T001", "$": "人口"}],
                        },
                    ],
                },
                "DATA_INF": {
                    "VALUE": [
                        {"@tab": "T001", "$": "126146099"},
                        {"@tab": "T001", "$": "125570000"},
                    ],
                },
            },
        }
        response = StatsDataResponse.model_validate(data)
        assert response.result.is_success
        values = response.get_data_values()
        assert len(values) == 2
        assert values[0].numeric_value == 126146099.0
        class_info = response.get_class_info()
        assert len(class_info) == 1
        assert class_info[0].id == "tab"


class TestDatasetInfo:
    """DatasetInfoモデルのテスト."""

    def test_valid_dataset_info(self) -> None:
        """データセット情報をパースできること."""
        data = {
            "@id": "DS001",
            "STATS_DATA_ID": "0003348423",
            "DATASET_NAME": "人口データセット",
            "OPEN": "1",
            "CREATED": "2021-01-01",
        }
        dataset = DatasetInfo.model_validate(data)
        assert dataset.id == "DS001"
        assert dataset.stats_data_id == "0003348423"
        assert dataset.dataset_name == "人口データセット"
        assert dataset.open == "1"


class TestDatasetListResponse:
    """DatasetListResponseモデルのテスト."""

    def test_valid_dataset_list_response(self) -> None:
        """データセットリストレスポンスをパースできること."""
        data = {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "正常に終了しました",
                "DATE": "2026-01-07T12:00:00.000+09:00",
            },
            "PARAMETER": {"LANG": "J"},
            "DATALIST_INF": {
                "NUMBER": 1,
                "DATASET_INF": [
                    {
                        "@id": "DS001",
                        "STATS_DATA_ID": "0003348423",
                        "DATASET_NAME": "人口データセット",
                    },
                ],
            },
        }
        response = DatasetListResponse.model_validate(data)
        assert response.result.is_success
        datasets = response.get_datasets()
        assert len(datasets) == 1
        assert datasets[0].id == "DS001"
