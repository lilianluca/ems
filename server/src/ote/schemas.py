from pydantic import Field

from src.core.schemas import APIBaseModel


class OTEQuarterHourPrice(APIBaseModel):
    """Schema for the OTE quarter-hour price data."""

    hour: int
    minute: int
    price_eur: float = Field(alias="priceEur")
    price_czk: float = Field(alias="priceCZK")
    level: str
    level_num: int = Field(alias="levelNum")
    level_num_96: int = Field(alias="levelNum96")


class OTEPricesResponse(APIBaseModel):
    """Schema for the OTE prices response."""

    hours_today: list[OTEQuarterHourPrice] = Field(alias="hoursToday")
    hours_tomorrow: list[OTEQuarterHourPrice] = Field(alias="hoursTomorrow")


class OTEFetchPricesResponse(APIBaseModel):
    """Schema for the fetch-prices endpoint response."""

    points_written: int
