"""e-Stat APIレスポンスモデル定義."""

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from e_stat_mcp.models.errors import ApiResult


def extract_text_value(v: Any) -> str | None:
    """辞書形式または文字列/数値から文字列値を抽出.

    e-Stat APIは一部のフィールドを {'@code': '...', '$': '値'} 形式で返す。
    この関数はそのような値から文字列を抽出する。

    Args:
        v: 入力値（辞書、文字列、数値、またはNone）

    Returns:
        抽出された文字列値、またはNone
    """
    if v is None:
        return None
    if isinstance(v, dict):
        return str(v.get("$", ""))
    return str(v)


class StatsTable(BaseModel):
    """統計表情報."""

    id: str = Field(..., alias="@id", description="統計表ID")
    stat_name: str = Field(..., alias="STAT_NAME", description="政府統計名称")
    gov_org: str = Field(..., alias="GOV_ORG", description="作成機関名")
    statistics_name: str | None = Field(None, alias="STATISTICS_NAME")
    title: str = Field(..., alias="TITLE", description="統計表名称")
    cycle: str | None = Field(None, alias="CYCLE", description="調査周期")
    survey_date: str | None = Field(None, alias="SURVEY_DATE", description="調査年月")
    open_date: str | None = Field(None, alias="OPEN_DATE", description="公開日")
    small_area: int | None = Field(None, alias="SMALL_AREA", description="小地域フラグ")
    main_category: str | None = Field(None, alias="MAIN_CATEGORY", description="大分類")
    sub_category: str | None = Field(None, alias="SUB_CATEGORY", description="小分類")
    overall_total_number: int | None = Field(None, alias="OVERALL_TOTAL_NUMBER")
    updated_date: str | None = Field(None, alias="UPDATED_DATE")
    description: str | None = Field(None, alias="DESCRIPTION")

    @field_validator(
        "stat_name",
        "gov_org",
        "title",
        "main_category",
        "sub_category",
        "cycle",
        "statistics_name",
        "description",
        mode="before",
    )
    @classmethod
    def extract_text(cls, v: Any) -> str | None:
        """辞書形式から文字列値を抽出."""
        return extract_text_value(v)

    @field_validator("survey_date", "open_date", "updated_date", mode="before")
    @classmethod
    def convert_date_to_str(cls, v: Any) -> str | None:
        """日付フィールドを文字列に変換（整数の場合も含む）."""
        return extract_text_value(v)


class StatsListResponse(BaseModel):
    """getStatsListレスポンス."""

    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict[str, Any] = Field(..., alias="PARAMETER")
    datalist_inf: dict[str, Any] | None = Field(None, alias="DATALIST_INF")

    def get_tables(self) -> list[StatsTable]:
        """統計表リストを取得.

        Returns:
            統計表のリスト。該当データなしの場合は空リスト。
        """
        if not self.datalist_inf:
            return []
        table_inf = self.datalist_inf.get("TABLE_INF", [])
        if isinstance(table_inf, dict):
            table_inf = [table_inf]
        if not isinstance(table_inf, list):
            return []
        return [StatsTable.model_validate(t) for t in table_inf]


class ClassItem(BaseModel):
    """分類項目.

    e-Stat APIは分類項目を2つの形式で返す:
    1. {'@code': '...', '@name': '...', '@level': '...'} - @name形式
    2. {'@code': '...', '$': '...', '@level': '...'} - $形式

    両方の形式に対応するため、model_validatorで事前に正規化する。
    """

    code: str = Field(..., alias="@code")
    name: str = Field(..., description="分類項目名称")
    level: str | None = Field(None, alias="@level")
    unit: str | None = Field(None, alias="@unit")
    parent_code: str | None = Field(None, alias="@parentCode")

    @model_validator(mode="before")
    @classmethod
    def normalize_name_field(cls, data: Any) -> Any:
        """@nameまたは$フィールドをnameに正規化.

        Raises:
            ValueError: @nameも$もnameも存在しない場合
        """
        if not isinstance(data, dict):
            return data

        # nameフィールドがまだ設定されていない場合
        if "name" not in data:
            # @nameフィールドがある場合
            if "@name" in data:
                data["name"] = data["@name"]
            # $フィールドがある場合
            elif "$" in data:
                data["name"] = data["$"]
            else:
                raise ValueError(
                    f"ClassItemに名称フィールドがありません: "
                    f"@name, $, nameのいずれかが必要です。data={data!r}"
                )

        return data


class ClassInfo(BaseModel):
    """分類情報."""

    id: str = Field(..., alias="@id")
    name: str = Field(..., alias="@name")
    items: list[ClassItem] = Field(default_factory=list, alias="CLASS")

    @field_validator("items", mode="before")
    @classmethod
    def normalize_items(cls, v: Any) -> list[Any]:
        """CLASSフィールドを正規化（単一辞書の場合はリストに変換）.

        Raises:
            ValueError: 予期しない型が渡された場合
        """
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        if isinstance(v, list):
            return v
        raise ValueError(
            f"CLASSフィールドに予期しない型が渡されました: type={type(v).__name__}, value={v!r}"
        )


class MetaInfoResponse(BaseModel):
    """getMetaInfoレスポンス."""

    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict[str, Any] = Field(..., alias="PARAMETER")
    class_inf: dict[str, Any] | None = Field(None, alias="CLASS_INF")

    def get_class_objects(self) -> list[ClassInfo]:
        """分類情報リストを取得.

        Returns:
            分類情報のリスト。該当データなしの場合は空リスト。
        """
        if not self.class_inf:
            return []
        class_obj = self.class_inf.get("CLASS_OBJ", [])
        if isinstance(class_obj, dict):
            class_obj = [class_obj]
        if not isinstance(class_obj, list):
            return []
        return [ClassInfo.model_validate(c) for c in class_obj]


class DataValue(BaseModel):
    """統計データ値."""

    tab: str = Field(..., alias="@tab", description="表章事項コード")
    cat01: str | None = Field(None, alias="@cat01", description="分類事項コード01")
    cat02: str | None = Field(None, alias="@cat02", description="分類事項コード02")
    cat03: str | None = Field(None, alias="@cat03", description="分類事項コード03")
    area: str | None = Field(None, alias="@area", description="地域コード")
    time: str | None = Field(None, alias="@time", description="時間軸コード")
    unit: str | None = Field(None, alias="@unit", description="単位")
    value: str = Field(..., alias="$", description="統計値")

    @property
    def numeric_value(self) -> float | None:
        """数値に変換（変換不可の場合はNone）."""
        # 欠損値を処理
        if self.value in ["-", "...", "x", "*", "…"]:
            return None
        try:
            return float(self.value.replace(",", ""))
        except (ValueError, AttributeError):
            return None


class StatsDataResponse(BaseModel):
    """getStatsDataレスポンス."""

    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict[str, Any] = Field(..., alias="PARAMETER")
    statistical_data: dict[str, Any] | None = Field(None, alias="STATISTICAL_DATA")

    def get_data_values(self) -> list[DataValue]:
        """データ値リストを取得.

        Returns:
            データ値のリスト。該当データなしの場合は空リスト。
        """
        if not self.statistical_data:
            return []
        data_inf = self.statistical_data.get("DATA_INF", {})
        if not isinstance(data_inf, dict):
            return []
        value_list = data_inf.get("VALUE", [])
        if isinstance(value_list, dict):
            value_list = [value_list]
        if not isinstance(value_list, list):
            return []
        return [DataValue.model_validate(v) for v in value_list]

    def get_class_info(self) -> list[ClassInfo]:
        """関連する分類情報を取得.

        Returns:
            分類情報のリスト。該当データなしの場合は空リスト。
        """
        if not self.statistical_data:
            return []
        class_inf = self.statistical_data.get("CLASS_INF", {})
        if not isinstance(class_inf, dict):
            return []
        class_obj = class_inf.get("CLASS_OBJ", [])
        if isinstance(class_obj, dict):
            class_obj = [class_obj]
        if not isinstance(class_obj, list):
            return []
        return [ClassInfo.model_validate(c) for c in class_obj]


class DatasetInfo(BaseModel):
    """データセット情報."""

    id: str = Field(..., alias="@id", description="データセットID")
    stats_data_id: str = Field(..., alias="STATS_DATA_ID", description="統計表ID")
    dataset_name: str = Field(..., alias="DATASET_NAME", description="データセット名")
    open: str | None = Field(None, alias="OPEN", description="公開状態")
    created: str | None = Field(None, alias="CREATED", description="作成日時")
    updated: str | None = Field(None, alias="UPDATED", description="更新日時")
    description: str | None = Field(None, alias="DESCRIPTION")


class DatasetListResponse(BaseModel):
    """refDatasetレスポンス（一覧）."""

    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict[str, Any] = Field(..., alias="PARAMETER")
    datalist_inf: dict[str, Any] | None = Field(None, alias="DATALIST_INF")

    def get_datasets(self) -> list[DatasetInfo]:
        """データセットリストを取得.

        Returns:
            データセットのリスト。該当データなしの場合は空リスト。
        """
        if not self.datalist_inf:
            return []
        dataset_inf = self.datalist_inf.get("DATASET_INF", [])
        if isinstance(dataset_inf, dict):
            dataset_inf = [dataset_inf]
        if not isinstance(dataset_inf, list):
            return []
        return [DatasetInfo.model_validate(d) for d in dataset_inf]
