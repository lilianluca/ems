from src.optimization.enums import PriceCategory
from src.sites.enums import RiskProfile

# Cílové úrovně SoC [%] podle rizikového profilu a cenové kategorie.
# Zdroj: Sodomka, BP, tabulka 5.1. Profil EXTREME vynechán — jeho odlišnost
# spočívá v odpojování spotřebičů, což tento model neřeší.
TARGET_SOC_PERCENT: dict[RiskProfile, dict[PriceCategory, float]] = {
    RiskProfile.LOW: {
        PriceCategory.EXTREMELY_LOW: 80.0,
        PriceCategory.LOW: 60.0,
        PriceCategory.AVERAGE: 40.0,
        PriceCategory.HIGH: 20.0,
    },
    RiskProfile.MEDIUM: {
        PriceCategory.EXTREMELY_LOW: 70.0,
        PriceCategory.LOW: 50.0,
        PriceCategory.AVERAGE: 30.0,
        PriceCategory.HIGH: 15.0,
    },
    RiskProfile.HIGH: {
        PriceCategory.EXTREMELY_LOW: 50.0,
        PriceCategory.LOW: 35.0,
        PriceCategory.AVERAGE: 25.0,
        PriceCategory.HIGH: 10.0,
    },
}

# Rezerva přičítaná k cílové úrovni při nabíjení (Sodomka, kap. 5.6.3).
# Brání tomu, aby drobná odchylka od predikce shodila SoC pod cíl.
TARGET_RESERVE_PERCENT = 10.0

# Percentilové hranice kategorií (Sodomka, kap. 5.6.2)
PERCENTILE_EXTREMELY_LOW = 10
PERCENTILE_LOW = 25
PERCENTILE_HIGH = 75
