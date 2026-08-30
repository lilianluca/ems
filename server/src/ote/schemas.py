from datetime import datetime

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


class OTEPriceRead(APIBaseModel):
    """A single quarter-hour block of the day-ahead spot price.

    `starts_at` is the instant the block begins, in UTC. The price holds constant
    for the whole block, which is why the frontend draws it as a step.
    """

    starts_at: datetime
    price_czk_mwh: float
    price_eur_mwh: float
    level: str


class OTEFetchPricesResponse(APIBaseModel):
    """Schema for the fetch-prices endpoint response."""

    points_written: int
