# modules/sectors/__init__.py
# Central registry — lists every available sector module.
# To add a new sector: create modules/sectors/<slug>.py and add it here.

from .banking import SECTOR_CONFIG as BANKING
from .fintech import SECTOR_CONFIG as FINTECH
from .financial_marketplace import SECTOR_CONFIG as FINANCIAL_MARKETPLACE
from .auto_ev import SECTOR_CONFIG as AUTO_EV
from .airlines import SECTOR_CONFIG as AIRLINES
from .airport_infrastructure import SECTOR_CONFIG as AIRPORT_INFRA
from .renewable_energy import SECTOR_CONFIG as RENEWABLE_ENERGY
from .it_services import SECTOR_CONFIG as IT_SERVICES
from .engineering_rd import SECTOR_CONFIG as ENGINEERING_RD
from .pharma import SECTOR_CONFIG as PHARMA
from .pharma_api import SECTOR_CONFIG as PHARMA_API
from .pharma_generics import SECTOR_CONFIG as PHARMA_GENERICS
from .pharma_cdmo import SECTOR_CONFIG as PHARMA_CDMO
from .pharma_specialty import SECTOR_CONFIG as PHARMA_SPECIALTY
from .biotech import SECTOR_CONFIG as BIOTECH
from .diagnostics import SECTOR_CONFIG as DIAGNOSTICS
from .hospitals import SECTOR_CONFIG as HOSPITALS
from .fmcg import SECTOR_CONFIG as FMCG
from .insurance import SECTOR_CONFIG as INSURANCE
from .nbfc import SECTOR_CONFIG as NBFC
from .telecom import SECTOR_CONFIG as TELECOM
from .metals_mining import SECTOR_CONFIG as METALS_MINING
from .coal_mining import SECTOR_CONFIG as COAL_MINING
from .real_estate import SECTOR_CONFIG as REAL_ESTATE
from .power_utilities import SECTOR_CONFIG as POWER_UTILITIES
from .power_generation import SECTOR_CONFIG as POWER_GENERATION
from .power_transmission import SECTOR_CONFIG as POWER_TRANSMISSION
from .power_distribution import SECTOR_CONFIG as POWER_DISTRIBUTION
from .power_integrated import SECTOR_CONFIG as POWER_INTEGRATED
from .capital_goods import SECTOR_CONFIG as CAPITAL_GOODS
from .industrial_automation import SECTOR_CONFIG as INDUSTRIAL_AUTOMATION
from .epc_engineering import SECTOR_CONFIG as EPC_ENGINEERING
from .electrical_equipment import SECTOR_CONFIG as ELECTRICAL_EQUIPMENT
from .heavy_engineering import SECTOR_CONFIG as HEAVY_ENGINEERING
from .defense_aerospace import SECTOR_CONFIG as DEFENSE_AEROSPACE
from .cement import SECTOR_CONFIG as CEMENT
from .chemicals import SECTOR_CONFIG as CHEMICALS
from .consumer_durables import SECTOR_CONFIG as CONSUMER_DURABLES
from .logistics import SECTOR_CONFIG as LOGISTICS
from .oil_gas import SECTOR_CONFIG as OIL_GAS
from .consumer_internet import SECTOR_CONFIG as CONSUMER_INTERNET
from .media import SECTOR_CONFIG as MEDIA
from .paints import SECTOR_CONFIG as PAINTS
from .port_infrastructure import SECTOR_CONFIG as PORT_INFRA
from .city_gas_distribution import SECTOR_CONFIG as CITY_GAS_DISTRIBUTION
from .spirits_tobacco import SECTOR_CONFIG as SPIRITS_TOBACCO
from .luxury_goods_jewelry import SECTOR_CONFIG as LUXURY_GOODS_JEWELRY
from .asset_management import SECTOR_CONFIG as ASSET_MANAGEMENT
from .hospitality import SECTOR_CONFIG as HOSPITALITY
from .market_infrastructure import SECTOR_CONFIG as MARKET_INFRASTRUCTURE
from .capital_markets import SECTOR_CONFIG as CAPITAL_MARKETS
from .textiles_apparel import SECTOR_CONFIG as TEXTILES_APPAREL
from .qsr_restaurants import SECTOR_CONFIG as QSR_RESTAURANTS
from .retail_apparel import SECTOR_CONFIG as RETAIL_APPAREL
from .tyre_manufacturing import SECTOR_CONFIG as TYRE_MANUFACTURING
from .railway_travel_services import SECTOR_CONFIG as RAILWAY_TRAVEL_SERVICES
from .generic import SECTOR_CONFIG as GENERIC

# Master registry: slug → config dict
SECTOR_REGISTRY: dict[str, dict] = {
    "banking":          BANKING,
    "fintech":          FINTECH,
    "financial_marketplace": FINANCIAL_MARKETPLACE,
    "auto_ev":          AUTO_EV,
    "airlines":         AIRLINES,
    "airport_infra":    AIRPORT_INFRA,
    "renewable_energy": RENEWABLE_ENERGY,
    "it_services":      IT_SERVICES,
    "engineering_rd":   ENGINEERING_RD,
    "pharma":           PHARMA,          # kept for backward compat — detector.py no longer emits this slug
    "pharma_api":       PHARMA_API,
    "pharma_generics":  PHARMA_GENERICS,
    "pharma_cdmo":      PHARMA_CDMO,
    "pharma_specialty": PHARMA_SPECIALTY,
    "biotech":          BIOTECH,
    "diagnostics":      DIAGNOSTICS,
    "hospitals":        HOSPITALS,
    "fmcg":             FMCG,
    "insurance":        INSURANCE,
    "nbfc":             NBFC,
    "telecom":          TELECOM,
    "metals_mining":    METALS_MINING,
    "coal_mining":      COAL_MINING,
    "real_estate":      REAL_ESTATE,
    "power_utilities":  POWER_UTILITIES,   # generic fallback — see detector.py
    "power_generation":   POWER_GENERATION,
    "power_transmission": POWER_TRANSMISSION,
    "power_distribution": POWER_DISTRIBUTION,
    "power_integrated":   POWER_INTEGRATED,
    "capital_goods":       CAPITAL_GOODS,   # kept for backward compat — detector.py no longer emits this slug
    "industrial_automation": INDUSTRIAL_AUTOMATION,
    "epc_engineering":       EPC_ENGINEERING,
    "electrical_equipment":  ELECTRICAL_EQUIPMENT,
    "heavy_engineering":     HEAVY_ENGINEERING,
    "defense_aerospace":     DEFENSE_AEROSPACE,
    "cement":              CEMENT,
    "chemicals":           CHEMICALS,
    "consumer_durables":   CONSUMER_DURABLES,
    "logistics":           LOGISTICS,
    "oil_gas":             OIL_GAS,
    "consumer_internet":   CONSUMER_INTERNET,
    "media":               MEDIA,
    "paints":              PAINTS,
    "port_infra":          PORT_INFRA,
    "city_gas_distribution": CITY_GAS_DISTRIBUTION,
    "spirits_tobacco":     SPIRITS_TOBACCO,
    "luxury_goods_jewelry": LUXURY_GOODS_JEWELRY,
    "asset_management":    ASSET_MANAGEMENT,
    "hospitality":         HOSPITALITY,
    "market_infrastructure": MARKET_INFRASTRUCTURE,
    "capital_markets":     CAPITAL_MARKETS,
    "textiles_apparel":    TEXTILES_APPAREL,
    "qsr_restaurants":     QSR_RESTAURANTS,
    "retail_apparel":      RETAIL_APPAREL,
    "tyre_manufacturing":  TYRE_MANUFACTURING,
    "railway_travel_services": RAILWAY_TRAVEL_SERVICES,
    "generic":          GENERIC,   # fallback — always last
}

def get_sector_config(slug: str) -> dict:
    """Return the config for a sector slug, falling back to generic."""
    return SECTOR_REGISTRY.get(slug, GENERIC)
