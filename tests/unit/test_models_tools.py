"""Unit tests for MCP tool models."""

import pytest
from pydantic import ValidationError

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


class TestSearchStatsRequest:
    """SearchStatsRequestのテスト."""

    def test_create_request_with_keyword(self) -> None:
        """キーワード検索リクエストを作成できること."""
        request = SearchStatsRequest(keyword="人口")
        assert request.keyword == "人口"
        assert request.stats_code is None
        assert request.survey_years is None
        assert request.limit == 100
        assert request.start_position == 1

    def test_create_request_with_all_params(self) -> None:
        """すべてのパラメータを指定してリクエストを作成できること."""
        request = SearchStatsRequest(
            keyword="国勢調査",
            stats_code="00200521",
            survey_years="2020-2023",
            limit=50,
            start_position=10,
        )
        assert request.keyword == "国勢調査"
        assert request.stats_code == "00200521"
        assert request.survey_years == "2020-2023"
        assert request.limit == 50
        assert request.start_position == 10

    def test_limit_validation(self) -> None:
        """limitのバリデーションが正しく動作すること."""
        # Valid range
        request = SearchStatsRequest(keyword="test", limit=1)
        assert request.limit == 1

        request = SearchStatsRequest(keyword="test", limit=100000)
        assert request.limit == 100000

        # Out of range
        with pytest.raises(ValidationError):
            SearchStatsRequest(keyword="test", limit=0)

        with pytest.raises(ValidationError):
            SearchStatsRequest(keyword="test", limit=100001)

    def test_start_position_validation(self) -> None:
        """start_positionのバリデーションが正しく動作すること."""
        request = SearchStatsRequest(keyword="test", start_position=1)
        assert request.start_position == 1

        with pytest.raises(ValidationError):
            SearchStatsRequest(keyword="test", start_position=0)


class TestSearchStatsResult:
    """SearchStatsResultのテスト."""

    def test_create_result(self) -> None:
        """検索結果を作成できること."""
        result = SearchStatsResult(
            table_id="0003410379",
            table_name="男女別人口",
            stat_name="国勢調査",
            survey_date="202010",
            gov_org="総務省",
        )
        assert result.table_id == "0003410379"
        assert result.table_name == "男女別人口"
        assert result.stat_name == "国勢調査"
        assert result.survey_date == "202010"
        assert result.gov_org == "総務省"

    def test_create_result_with_optional_fields(self) -> None:
        """オプションフィールドなしで検索結果を作成できること."""
        result = SearchStatsResult(
            table_id="0003410379",
            table_name="男女別人口",
            stat_name="国勢調査",
            gov_org="総務省",
        )
        assert result.survey_date is None


class TestGetStatsDataRequest:
    """GetStatsDataRequestのテスト."""

    def test_create_request_with_id_only(self) -> None:
        """統計表IDのみでリクエストを作成できること."""
        request = GetStatsDataRequest(stats_data_id="0003410379")
        assert request.stats_data_id == "0003410379"
        assert request.cd_tab is None
        assert request.cd_cat01 is None
        assert request.limit == 10000

    def test_create_request_with_filters(self) -> None:
        """フィルタ条件付きでリクエストを作成できること."""
        request = GetStatsDataRequest(
            stats_data_id="0003410379",
            cd_tab="001",
            cd_cat01="A",
            cd_area="00000",
            cd_time="202010",
            limit=1000,
        )
        assert request.cd_tab == "001"
        assert request.cd_cat01 == "A"
        assert request.cd_area == "00000"
        assert request.cd_time == "202010"
        assert request.limit == 1000


class TestStatsDataItem:
    """StatsDataItemのテスト."""

    def test_create_item(self) -> None:
        """統計データ項目を作成できること."""
        item = StatsDataItem(
            tab_name="人口",
            category_names={"cat01": "男性"},
            area_name="全国",
            time_name="2020年",
            value=63000000.0,
            value_raw="63000000",
            unit="人",
        )
        assert item.tab_name == "人口"
        assert item.category_names == {"cat01": "男性"}
        assert item.area_name == "全国"
        assert item.time_name == "2020年"
        assert item.value == 63000000.0
        assert item.value_raw == "63000000"
        assert item.unit == "人"

    def test_create_item_with_null_value(self) -> None:
        """欠損値を含む統計データ項目を作成できること."""
        item = StatsDataItem(
            tab_name="人口",
            value=None,
            value_raw="-",
        )
        assert item.value is None
        assert item.value_raw == "-"


class TestStatsDataResult:
    """StatsDataResultのテスト."""

    def test_create_result(self) -> None:
        """統計データ結果を作成できること."""
        result = StatsDataResult(
            total_count=100,
            returned_count=10,
            data=[
                StatsDataItem(
                    tab_name="人口",
                    value=126000000.0,
                    value_raw="126000000",
                )
            ],
            has_next=True,
            next_start_position=11,
        )
        assert result.total_count == 100
        assert result.returned_count == 10
        assert len(result.data) == 1
        assert result.has_next is True
        assert result.next_start_position == 11

    def test_create_result_has_next_true(self) -> None:
        """次ページが存在する場合のテスト（T001）.

        Given: 総件数がlimitを超えるデータ
        When: StatsDataResultを作成する
        Then: has_next=True, next_start_positionが正しく設定される
        """
        result = StatsDataResult(
            total_count=25000,
            returned_count=10000,
            data=[],
            has_next=True,
            next_start_position=10001,
        )
        assert result.has_next is True
        assert result.next_start_position == 10001

    def test_create_result_has_next_false(self) -> None:
        """次ページが存在しない場合のテスト（T002）.

        Given: 総件数がlimit以下のデータ
        When: StatsDataResultを作成する
        Then: has_next=False, next_start_position=None
        """
        result = StatsDataResult(
            total_count=5000,
            returned_count=5000,
            data=[],
            has_next=False,
            next_start_position=None,
        )
        assert result.has_next is False
        assert result.next_start_position is None

    def test_create_result_empty_data(self) -> None:
        """空の結果の場合のテスト（T003 - 境界条件）.

        Given: 空の結果（returned_count=0）
        When: StatsDataResultを作成する
        Then: has_next=False, next_start_position=None
        """
        result = StatsDataResult(
            total_count=0,
            returned_count=0,
            data=[],
            has_next=False,
            next_start_position=None,
        )
        assert result.has_next is False
        assert result.next_start_position is None
        assert result.returned_count == 0

    def test_create_result_exactly_limit(self) -> None:
        """ちょうどlimit件の場合のテスト（T003 - 境界条件）.

        Given: 総件数とreturned_countが等しい
        When: StatsDataResultを作成する
        Then: has_next=False, next_start_position=None
        """
        result = StatsDataResult(
            total_count=10000,
            returned_count=10000,
            data=[],
            has_next=False,
            next_start_position=None,
        )
        assert result.has_next is False
        assert result.next_start_position is None

    def test_create_result_last_page(self) -> None:
        """最終ページの場合のテスト（T003 - 境界条件）.

        Given: 最終ページのデータ（start_position=20001, returned_count=5000, total=25000）
        When: StatsDataResultを作成する
        Then: has_next=False, next_start_position=None
        """
        result = StatsDataResult(
            total_count=25000,
            returned_count=5000,
            data=[],
            has_next=False,
            next_start_position=None,
        )
        assert result.has_next is False
        assert result.next_start_position is None


class TestGetMetaInfoRequest:
    """GetMetaInfoRequestのテスト."""

    def test_create_request(self) -> None:
        """メタ情報取得リクエストを作成できること."""
        request = GetMetaInfoRequest(stats_data_id="0003410379")
        assert request.stats_data_id == "0003410379"


class TestClassItemInfo:
    """ClassItemInfoのテスト."""

    def test_create_class_item_info(self) -> None:
        """分類項目情報を作成できること."""
        item = ClassItemInfo(
            code="001",
            name="人口",
            level="1",
            unit="人",
        )
        assert item.code == "001"
        assert item.name == "人口"
        assert item.level == "1"
        assert item.unit == "人"

    def test_create_class_item_info_minimal(self) -> None:
        """最小限のフィールドで分類項目情報を作成できること."""
        item = ClassItemInfo(
            code="001",
            name="人口",
        )
        assert item.code == "001"
        assert item.name == "人口"
        assert item.level is None
        assert item.unit is None


class TestMetaInfoResult:
    """MetaInfoResultのテスト."""

    def test_create_meta_info_result(self) -> None:
        """メタ情報結果を作成できること."""
        result = MetaInfoResult(
            class_id="tab",
            class_name="表章事項",
            items=[
                ClassItemInfo(code="001", name="人口"),
                ClassItemInfo(code="002", name="面積"),
            ],
        )
        assert result.class_id == "tab"
        assert result.class_name == "表章事項"
        assert len(result.items) == 2


class TestListDatasetsRequest:
    """ListDatasetsRequestのテスト."""

    def test_create_request_without_filter(self) -> None:
        """フィルタなしでリクエストを作成できること."""
        request = ListDatasetsRequest()
        assert request.stats_data_id is None

    def test_create_request_with_filter(self) -> None:
        """統計表IDフィルタ付きでリクエストを作成できること."""
        request = ListDatasetsRequest(stats_data_id="0003410379")
        assert request.stats_data_id == "0003410379"


class TestDatasetResult:
    """DatasetResultのテスト."""

    def test_create_dataset_result(self) -> None:
        """データセット結果を作成できること."""
        result = DatasetResult(
            dataset_id="DS001",
            dataset_name="人口データセット",
            stats_data_id="0003410379",
            is_public=True,
            description="2020年国勢調査人口データ",
        )
        assert result.dataset_id == "DS001"
        assert result.dataset_name == "人口データセット"
        assert result.stats_data_id == "0003410379"
        assert result.is_public is True
        assert result.description == "2020年国勢調査人口データ"


class TestGetDatasetDataRequest:
    """GetDatasetDataRequestのテスト."""

    def test_create_request(self) -> None:
        """データセットデータ取得リクエストを作成できること."""
        request = GetDatasetDataRequest(dataset_id="DS001")
        assert request.dataset_id == "DS001"
        assert request.limit == 10000
        assert request.start_position == 1

    def test_create_request_with_pagination(self) -> None:
        """ページネーション付きでリクエストを作成できること."""
        request = GetDatasetDataRequest(
            dataset_id="DS001",
            limit=5000,
            start_position=100,
        )
        assert request.limit == 5000
        assert request.start_position == 100
