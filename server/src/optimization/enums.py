import enum


class PriceCategory(enum.StrEnum):
    """Enumeration of price categories."""

    EXTREMELY_LOW = "extremely_low"
    LOW = "low"
    AVERAGE = "average"
    HIGH = "high"
