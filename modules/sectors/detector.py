# modules/sectors/detector.py
"""
Sector Detection Layer
======================
Input  : company_name, industry, sector (from yfinance), business_description
Output : sector slug (matches a key in SECTOR_REGISTRY)

Detection strategy (ordered by precision):
  1. Explicit yfinance industry/sector → keyword map  (fast, deterministic)
  2. Business description keyword scan                (catches edge cases)
  3. LLM fallback via a compact prompt               (handles novel cases)
  4. "generic" if all else fails                     (safe default)
"""

from __future__ import annotations
import re

# ── Keyword → slug map ────────────────────────────────────────────────────────
# Each entry: list of substrings to search for (case-insensitive) in the
# combined "sector|industry|description" string. First match wins.
_RULES: list[tuple[str, list[str]]] = [
    ("banking", [
        "bank", "banking", "casa", "npa", "net interest margin",
        "commercial bank", "private bank", "public sector bank", "psu bank",
        "hdfc bank", "icici bank", "state bank of india", "kotak bank", "axis bank",
        # NOTE: bare "sbi" used to be here — removed. It falsely matched
        # "SBI Life Insurance", "SBI Cards", "SBI General Insurance", and
        # "SBI Mutual Fund" (separately-listed companies, not the bank),
        # via \bsbi\w*. The full-name phrase above still catches the actual
        # bank, and it's redundant anyway since "State Bank Of India" also
        # contains "bank" which already matches on its own.
    ]),
    ("financial_marketplace", [
        # Must come BEFORE "insurance" below — an aggregator/broker's
        # yfinance industry tag is literally "Insurance Brokers", which
        # contains "insurance" and would otherwise match the insurer rule
        # first. A broker/aggregator sells other companies' products for a
        # commission and never holds underwriting risk — see
        # financial_marketplace.py for why that needs a different
        # moat/bull/bear framework entirely.
        "pb fintech", "policybazaar", "paisabazaar",
        "insurance broker", "insurance aggregator", "insurance marketplace",
        "loan marketplace", "financial products marketplace",
    ]),
    ("insurance", [
        "insurance", "life insurance", "general insurance", "reinsurance",
        "gdp premium", "policyholder", "solvency ratio",
        # NOTE: bare "lic" used to be here — removed. \blic\w* falsely
        # matched "license", "licensing", "licensed technology" — common
        # in tech/pharma/industrial business descriptions. "life insurance"
        # above already generically covers Life Insurance Corporation of
        # India without needing the risky abbreviation.
    ]),
    ("nbfc", [
        "nbfc", "non-banking financial", "microfinance", "mfi",
        "credit services",  # standard yfinance industry tag for most Indian
        # NBFC lenders (Bajaj Finance, Muthoot, Cholamandalam etc. are all
        # tagged this way) — without it these fell through to description.
        "asset finance", "gold loan", "housing finance", "vehicle finance",
        "bajaj finance", "muthoot", "chola",
    ]),
    ("fintech", [
        "fintech", "payment", "digital payment", "upi", "wallet",
        "neobank", "lending platform", "buy now pay later", "bnpl",
        "paytm", "razorpay", "phonepe",
    ]),
    ("renewable_energy", [
        "renewable", "solar", "wind energy", "green energy",
        "clean energy", "photovoltaic", "power generation renewable",
        "adani green", "tata power solar",
    ]),
    ("power_transmission", [
        # Split out of power_utilities — see power_transmission.py for why a
        # pure transmission company needs different moat/bull/bear framing
        # than a generator or distributor. Keep this narrow: don't add
        # generic "electricity"/"power" terms here, those stay in the
        # power_utilities fallback below.
        "power grid corporation", "power grid", "power transmission",
        "transmission monopoly", "interstate transmission",
        "adani energy solutions", "adani transmission",
    ]),
    ("power_generation", [
        "ntpc", "adani power", "jsw energy", "thermal power",
        "coal power", "power generation company", "independent power producer",
        "hydro power generation", "gas power generation",
    ]),
    ("power_distribution", [
        "torrent power", "cesc", "electricity distribution",
        "power distribution company", "discom",
    ]),
    ("power_integrated", [
        "tata power", "integrated power utility", "integrated utility",
    ]),
    ("city_gas_distribution", [
        # Must come BEFORE power_utilities below — yfinance tags these
        # "Utilities - Regulated Gas", whose literal substring "utilities -
        # regulated" would otherwise match the power_utilities fallback and
        # apply an electricity-generator framing (PLF, fuel-linkage) to a
        # PNG/CNG city-gas distributor. See city_gas_distribution.py
        # docstring for why it needs its own module.
        "city gas distribution", "cgd licence", "cgd license",
        "piped natural gas", "cng station", "cng vehicle",
        "utilities - regulated gas",
        "indraprastha gas", "mahanagar gas", "gujarat gas", "adani total gas",
        "gail gas",
        # NOTE: bare "city gas", "png", and "gas distribution" deliberately
        # excluded — too easily match GAIL India's own "gas transmission
        # and distribution" business description, which belongs to
        # oil_gas (GAIL is a transmission/marketing major, not a
        # geographic-licence CGD retailer).
    ]),
    ("power_utilities", [
        # Narrowed fallback — only for power companies that don't clearly
        # match one of the value-chain-specific rules above (e.g. a smaller
        # or diversified utility where generation/transmission/distribution
        # split can't be determined from name/industry text alone).
        "power utility", "hydro power", "electricity generation",
        "regulated electric", "diversified utilities",
        "utilities - regulated", "electric utility",
    ]),
    ("tyre_manufacturing", [
        # Must come BEFORE auto_ev below — auto_ev's "auto parts" keyword
        # would otherwise catch tyre makers, applying vehicle-OEM framing
        # (ASP, EV mix, model launches) to a component manufacturer whose
        # economics are driven by OEM-vs-replacement channel mix and
        # natural rubber prices instead. See tyre_manufacturing.py.
        "tyre", "tire manufactur", "mrf limited", "mrf ltd",
        "apollo tyres", "ceat limited", "ceat ltd", "jk tyre",
        "balkrishna industries",
    ]),
    ("auto_ev", [
        "automobile", "automotive", "auto oem", "vehicle manufacturer",
        "electric vehicle", "ev manufacturer", "two wheeler", "four wheeler",
        "commercial vehicle", "tractor", "battery electric",
        "auto manufacturer", "auto parts", "recreational vehicle",
        "maruti", "tata motors", "mahindra & mahindra", "hero motocorp", "ola electric",
    ]),
    ("airport_infra", [
        # Distinct from "airlines" above — an airport operator owns/runs
        # the airport itself under a regulated concession, it doesn't fly
        # planes. Same gap as airlines had: was falling through to
        # "generic" with no keyword rule at all. See
        # airport_infrastructure.py docstring for why it needs its own
        # module rather than reusing the airlines one.
        "airport", "airports", "airport operator", "airport infrastructure",
        "airport services", "aviation infrastructure",
        "gmr", "gmr airports", "gmr infrastructure",
        "adani airport", "adani airport holdings",
    ]),
    ("airlines", [
        # Was previously unclassified — fell all the way through to
        # "generic", which uses a normal-industrial D/E>1.5x red-flag
        # threshold and generic bull/bear/moat text. Airlines need their
        # own module: see airlines.py docstring for why (Ind AS 116 lease
        # capitalisation structurally inflates reported D/E for any
        # lease-heavy carrier — the Indian norm).
        "airline", "airlines", "aviation", "scheduled air transport",
        "low-cost carrier", "regional airline",
        "indigo", "interglobe aviation", "spicejet", "air india",
        "vistara", "akasa air", "go first", "goair",
    ]),
    ("engineering_rd", [
        "l&t technology services", "ltts", "tata technologies", "kpit",
        "kpit technologies", "cyient", "einfochips",
        "engineering research and development", "er&d", "engineering r&d",
        "product engineering services", "engineering design services",
        "digital engineering services", "embedded engineering services",
        "automotive engineering services",
        # NOTE: this rule must stay ABOVE it_services below — first match
        # wins, and it_services' generic "information technology"/"it
        # services" keywords would otherwise catch these companies first
        # via their yfinance industry tag, before their name/description
        # ever gets checked.
    ]),
    ("it_services", [
        "information technology", "it services", "software services",
        "bpo", "it consulting", "digital transformation",
        "tcs", "infosys", "wipro", "hcl tech", "tech mahindra",
    ]),
    ("railway_travel_services", [
        # A single, structurally unique company (an exclusive government-
        # granted railway ticketing/catering/tourism monopoly) — was
        # previously falling through to "generic", and was also at risk of
        # being misclassified into "hospitals" via a since-removed bare
        # "hospital" keyword that accidentally matched "hospitality" (a
        # word IRCTC's own business description legitimately uses for its
        # catering/tourism services). See railway_travel_services.py
        # docstring for the full reasoning.
        "irctc", "indian railway catering", "indian railway catering and tourism",
        "railway e-ticketing", "railway ticketing", "railway catering",
        "rail neer", "bharat gaurav", "state teerth",
    ]),
    ("hospitals", [
        "apollo hospitals", "fortis healthcare", "max healthcare",
        "narayana health", "aster dm healthcare", "krishna institute of medical",
        "rainbow children's medicare", "rainbow childrens medicare",
        "global health limited", "medanta",
        "hospital chain", "hospital group", "hospital network",
        "hospital bed", "hospital admission", "corporate hospital",
        "private hospital", "tertiary care hospital", "super specialty hospital",
        "healthcare delivery", "medical care facilit",
        "multi-specialty hospital", "multispecialty hospital",
        # NOTE: bare "hospital" used to be here — removed. The \b...\w*
        # matching used to build these patterns means "hospital" also
        # matches "hospitality" (a completely unrelated word about
        # tourism/catering/lodging, not medical hospitals) since
        # "hospital" is a literal text-prefix of "hospitality". A company
        # like IRCTC, whose own business description legitimately talks
        # about catering and "hospitality" services, was getting
        # misclassified into this sector purely because of that shared
        # prefix. The specific phrases above still catch genuine hospital
        # companies (via name/context) without that false-positive.
    ]),
    ("pharma_cdmo", [
        "syngene international", "suven pharma", "cohance lifesciences",
        "cdmo", "crams", "contract research and manufacturing",
        "contract development and manufacturing",
        "contract manufacturing organi",
        # Must come before diagnostics below — Syngene and other CDMOs are
        # commonly tagged "Diagnostics & Research" by yfinance (an
        # ambiguous catch-all industry label), which would otherwise match
        # the diagnostics rule first and misroute a CDMO into a lab-
        # services sector it has nothing to do with.
    ]),
    ("diagnostics", [
        "dr. lal pathlabs", "dr lal pathlabs", "metropolis healthcare",
        "thyrocare technologies", "vijaya diagnostic", "krsnaa diagnostics",
        "diagnostic", "pathology", "diagnostics & research",
        "clinical laboratory", "diagnostic laboratory", "pathology lab",
    ]),
    ("pharma_api", [
        "divi's laboratories", "laurus labs", "granules india",
        "aarti drugs", "neuland laboratories",
        "active pharmaceutical", "bulk drug", "api manufactur",
        # NOTE: bare "api" deliberately excluded — \bapi\w* falsely
        # matched "API integration" in tech/fintech descriptions
        # (Application Programming Interface, not Active Pharmaceutical
        # Ingredient). "active pharmaceutical" and "api manufactur" above
        # already cover genuine API mentions without that ambiguity.
    ]),
    ("biotech", [
        "biocon limited", "bharat biotech", "panacea biotec",
        "biotech", "biologics", "biosimilar",
    ]),
    ("pharma_specialty", [
        "specialty pharma", "specialty pharmaceutical",
    ]),
    ("pharma_generics", [
        "pharmaceutical", "pharma", "drug", "generic medicine",
        "sun pharma", "dr reddy", "cipla",
        # Fallback/default pharma bucket — anything pharma-related that
        # doesn't match a more specific rule above lands here, since
        # generic formulation is the most common Indian pharma business
        # model. Bare "divi" deliberately excluded — \bdivi\w* falsely
        # matched "dividend", "dividend yield", "divisive" in virtually
        # any company's financial description; the full name "divi's
        # laboratories" above (routed to pharma_api) is unambiguous.
    ]),
    ("spirits_tobacco", [
        # Must come BEFORE fmcg below — yfinance tags virtually every
        # company in this space with the bare sector label "Consumer
        # Defensive", the same GICS supersector as staples like HUL/Nestle,
        # which the fmcg rule's "consumer defensive" keyword would
        # otherwise catch first. Spirits and tobacco carry a materially
        # different risk profile (excise duty, advertising bans,
        # litigation, ESG exclusion) — see spirits_tobacco.py docstring.
        "united spirits", "united breweries", "godfrey phillips",
        "vst industries", "radico khaitan", "globus spirits",
        "alcoholic beverage", "spirits & beverages", "distillery",
        "brewery", "cigarette manufactur", "tobacco product",
    ]),
    ("fmcg", [
        "fmcg", "fast moving consumer goods", "consumer staples",
        "packaged foods", "personal care", "household products",
        "hindustan unilever", "nestle", "itc limited", "dabur",
        "consumer defensive",
        # NOTE: bare "hul" removed — \bhul\w* falsely matched "hull" (e.g.
        # ship/tank hull fabrication in industrial descriptions);
        # "hindustan unilever" above already covers it unambiguously. Bare
        # "itc" removed too — \bitc\w* falsely matched "ITC-HS code" (an
        # international trade classification code, common in exporter
        # descriptions); replaced with "itc limited" for the actual company.
    ]),
    ("telecom", [
        "telecom", "telecommunications", "mobile services", "broadband",
        "spectrum", "arpu", "airtel", "reliance jio", "vodafone idea",
    ]),
    ("coal_mining", [
        # This used to be a bare "coal india" entry inside the metals_mining
        # rule below — meaning Coal India (and its subsidiaries) were being
        # classified into the diversified steel/aluminium/zinc metals module,
        # producing moat/bull/bear text about "diversified commodity
        # exposure", aluminium, zinc-lead-silver etc. that has nothing to do
        # with a coal producer. Split into its own rule so it gets the
        # dedicated coal_mining module instead (reserves/licensing moat,
        # FSA/e-auction pricing, dividend-yield bull case, renewable-
        # transition bear case). Keep this narrow and specific — do NOT add
        # "coal power"/"coal-fired"/"thermal power" here, those correctly
        # belong to power_utilities above and must keep matching there.
        "coal india", "coal mining", "coal miner", "coal producer",
        "mahanadi coalfields", "singareni collieries",
    ]),
    ("metals_mining", [
        "metal", "mining", "steel", "aluminium", "copper", "iron ore",
        "zinc", "tata steel", "jsw steel", "vedanta",
        "hindalco",
    ]),
    ("real_estate", [
        "real estate", "realty", "property developer", "residential project",
        "commercial property", "real estate investment trust", "dlf",
        "godrej properties", "oberoi realty", "prestige estates",
        # NOTE: bare "reit" removed — \breit\w* falsely matched
        # "reiterate"/"reiterated" (extremely common in earnings
        # commentary — "management reiterated guidance..."). Replaced with
        # the spelled-out term, which is how REITs are actually described
        # in business summaries anyway.
    ]),
    ("industrial_automation", [
        "abb india", "abb ltd", "abb limited", "siemens limited", "siemens india",
        "honeywell automation", "honeywell india",
        "industrial automation", "factory automation", "process automation",
        "digital industries",  # Siemens' automation business segment name
        "motion control", "grid technology", "electrification technology",
        # Must come before the generic epc_engineering/heavy_engineering
        # catch-alls below — these are product/software businesses, not
        # project-execution or manufacturing-heavy businesses, even though
        # yfinance may tag them with a generic "Electrical Equipment &
        # Parts" or "Specialty Industrial Machinery" industry label.
    ]),
    ("defense_aerospace", [
        "hindustan aeronautics", "bharat electronics limited", "bharat dynamics",
        "mazagon dock", "garden reach shipbuilders", "cochin shipyard",
        "beml limited", "beml ltd", "astra microwave", "data patterns",
        "paras defence", "defence & aerospace", "defense & aerospace",
        "defence electronics", "defense electronics", "defence shipbuilding",
        "defense shipbuilding", "aerospace & defence", "aerospace & defense",
        "military aircraft", "combat aircraft", "missile systems manufacturer",
        # Must come before industrial_automation/epc_engineering/heavy_engineering
        # below — yfinance often tags these under a generic "Aerospace &
        # Defense" or "Specialty Industrial Machinery" industry label, which
        # would otherwise fall through to a generic capital-goods bucket and
        # miss the sector's defining trait: revenue concentrated in a single
        # government customer, not open-market competition.
    ]),
    ("epc_engineering", [
        "engineers india", "kec international", "thermax limited", "thermax ltd",
        "larsen & toubro", "l&t limited", "l&t construction",
        "engineering & construction", "epc contractor", "epc project", "turnkey project",
        # NOTE: "l&t" alone is deliberately excluded here — bare \bl&t\w*
        # would match inside "l&t technology services"/"ltts" descriptions
        # too, but that rule already sits above (in engineering_rd) and
        # wins first since it's checked earlier in the list, so this isn't
        # actually a conflict — kept explicit for clarity.
    ]),
    ("electrical_equipment", [
        "havells", "havells india", "polycab", "polycab india",
        "kei industries", "wires and cables", "wires & cables",
        "switchgear", "fmeg", "fast moving electrical goods",
        # NOTE: Havells moved here from consumer_durables — its core
        # business (wires & cables, switchgear) is a brand/distribution
        # electrical-equipment model, not a consumer-appliance model, even
        # though it also owns Lloyd (AC/appliances). This rule sits above
        # consumer_durables below, so it wins first for Havells.
    ]),
    ("heavy_engineering", [
        "bhel", "bharat heavy electricals", "triveni turbine", "triveni engineering",
        "cummins india", "cummins ltd", "cummins limited",
        "heavy engineering", "turbine manufacturer", "wind turbine",
        "power equipment manufacturer", "diesel engine manufacturer", "suzlon",
    ]),
    ("epc_engineering", [
        # Generic capital-goods catch-all — anything that still says
        # "capital goods" / "industrial machinery" / "industrial
        # conglomerate" without matching a more specific company name or
        # driver above lands in EPC/Engineering, since project-execution
        # is the most common Indian capital-goods business model (mirrors
        # how pharma_generics is the default pharma bucket).
        "capital goods", "industrial machinery", "industrial conglomerate",
        "specialty industrial machinery",
    ]),
    ("cement", [
        "cement", "cement manufacturing", "building materials",
        "ultratech", "ambuja cement", "acc limited", "shree cement",
        "dalmia bharat", "jk cement",
    ]),
    ("oil_gas", [
        "oil & gas", "oil and gas", "petroleum refining", "upstream oil",
        "downstream oil", "oil marketing company", "lng", "crude oil",
        "reliance industries", "ongc", "indian oil", "bharat petroleum",
        "hindustan petroleum", "gail india",
    ]),
    ("paints", [
        # Must come BEFORE chemicals below — yfinance tags decorative
        # paint majors "Specialty Chemicals" (a manufacturing-process
        # label), which would otherwise match the chemicals rule first and
        # apply commodity-price-taker, through-cycle EV/EBITDA framing to a
        # branded, dealer-network, pricing-power consumer business. See
        # paints.py docstring for the full reasoning.
        "asian paints", "berger paints", "kansai nerolac", "akzo nobel india",
        "shalimar paints", "indigo paints",
        "decorative paint", "industrial paint manufactur", "paint manufactur",
    ]),
    ("chemicals", [
        "chemical",  # bare keyword — catches plain yfinance industry/sector
        # labels like "Chemicals" that the more specific multi-word phrases
        # below don't cover. Word-boundary regex means this won't falsely
        # match "petrochemical" or "biochemical" (no boundary before
        # "chemical" in those words), so it's safe to add unqualified.
        "specialty chemical", "chemical manufacturing",
        "agrochemical", "fertilizer", "dyes and pigments", "basic chemicals",
        "srf limited", "aarti industries", "deepak nitrite", "pi industries",
        "upl limited", "tata chemicals",
    ]),
    ("consumer_durables", [
        "consumer durables", "consumer electronics", "home appliance",
        "furnishings", "houseware", "voltas", "whirlpool india",
        "crompton greaves consumer", "blue star limited", "symphony limited",
        # NOTE: "havells" removed — moved to electrical_equipment above.
        # Havells' core business (wires & cables, switchgear) is a brand/
        # distribution electrical-equipment model; the electrical_equipment
        # rule sits earlier in this list and wins first for it now.
    ]),
    ("port_infra", [
        # Must come BEFORE logistics below — a port operator's own
        # description repeatedly uses the word "logistics", and yfinance
        # may tag it "Marine Shipping", either of which would otherwise
        # match the freight-forwarder/courier rule first. See
        # port_infrastructure.py docstring for why a port/terminal
        # operator needs its own module (concession economics, locational
        # scarcity moat) rather than reusing the asset-light courier one.
        "port operator", "port infrastructure", "marine shipping",
        "container terminal", "port & sez", "ports & sez",
        "adani ports", "jnpt", "deendayal port", "chennai port",
        "krishnapatnam port", "gangavaram port",
    ]),
    ("logistics", [
        "logistics", "freight", "courier", "supply chain services",
        "warehousing", "container corporation", "concor", "blue dart",
        "delhivery", "mahindra logistics", "vrl logistics",
    ]),
    # saas → it_services; consumer internet/e-commerce → its own sector
    # (previously both were folded into "fintech", which conflates a
    # payments/lending business with a delivery/marketplace platform —
    # two genuinely different business models with different weight configs)
    ("it_services", [
        "saas", "software as a service", "cloud software", "b2b software",
    ]),
    ("consumer_internet", [
        "consumer internet", "e-commerce", "marketplace platform",
        "internet retail",  # standard yfinance industry tag for e-commerce
        # companies — distinct from "online retail" already below, which
        # doesn't match it as a substring.
        "food delivery", "quick commerce", "online retail",
        "zomato", "eternal", "swiggy", "nykaa", "meesho",
    ]),
    ("media", [
        "broadcast",  # \w* suffix matching means this alone covers
        # "broadcast", "broadcasting", "broadcaster" — e.g. "TV18
        # Broadcast Limited".
        "television network", "tv channel",
        "media conglomerate", "entertainment network", "news network",
        "gec",  # standard industry shorthand for "General Entertainment
        # Channel" — the Indian broadcasting term for a mainstream
        # Hindi/regional entertainment channel bouquet.
        "film production", "content production", "film studio",
        "multiplex", "cinema exhibition", "dth", "direct-to-home",
        "print media", "publishing house",
        "network18", "tv18", "zee entertainment", "sun tv network",
        "pvr inox", "dish tv", "hathway", "den networks", "saregama",
        "eros international", "balaji telefilms",
        # NOTE: bare "media" is intentionally NOT included here — \bmedia\w*
        # would false-positive on "social media" mentions inside fintech/
        # consumer-internet marketing descriptions and on "media" used
        # generically (e.g. "trade media", "print/media outreach") in
        # unrelated companies' business summaries. The specific phrases
        # and company names above are precise enough to avoid that.
    ]),
    ("luxury_goods_jewelry", [
        # Was previously falling through to "generic". See
        # luxury_goods_jewelry.py docstring for the gold-price-pass-through
        # and working-capital reasoning that generic industrial framing
        # misses for this sector.
        "titan company", "kalyan jewellers", "pc jeweller", "tribhovandas bhimji",
        "jewellery retail", "jewelry retail", "jewellery manufactur",
        "jewelry stores", "luxury goods", "watches & eyewear",
    ]),
    ("asset_management", [
        # Was previously falling through to "generic". See
        # asset_management.py docstring — AUM/expense-ratio economics have
        # nothing in common with a generic industrial or even a generic
        # financial-services framing.
        # NOTE: "asset management" (bare, no "compan" suffix requirement)
        # matches yfinance's own plain "Asset Management" industry tag —
        # a previous draft of this rule required a literal "compan" suffix
        # that would never actually match that tag.
        "asset management", "mutual fund", "hdfc amc",
        "nippon life india asset management", "uti asset management",
        "aditya birla sun life amc", "sbi funds management",
        "average assets under management",
    ]),
    ("hospitality", [
        # Was previously falling through to "generic". See hospitality.py
        # docstring — RevPAR/occupancy/ARR economics have no equivalent in
        # a generic industrial metric set. "lodging" is yfinance's own
        # plain industry tag for this group.
        "indian hotels company", "taj hotels", "eih limited", "oberoi hotels",
        "lemon tree hotels", "chalet hotels", "lodging", "hotel chain",
        "hospitality chain", "revpar",
    ]),
    ("market_infrastructure", [
        # Must come before capital_markets below — a broker's yfinance
        # industry tag ("Capital Markets") is distinct from an exchange's
        # own tag ("Financial Data & Stock Exchanges"), so keeping the
        # exact tag phrase here avoids any ambiguity between the two
        # rules. See market_infrastructure.py docstring for why an
        # exchange/depository needs different framing than a broker.
        "financial data & stock exchanges", "financial data & stock exchange",
        "stock exchanges", "bse limited", "bse ltd", "national stock exchange",
        "nse india", "central depository services", "cdsl",
        "multi commodity exchange", "stock exchange operator",
        "securities depository",
    ]),
    ("capital_markets", [
        # "capital markets" (bare) matches yfinance's own plain "Capital
        # Markets" industry tag used for brokers like Angel One, ICICI
        # Securities, Motilal Oswal.
        "capital markets", "angel one", "icici securities",
        "motilal oswal financial", "iifl securities", "5paisa",
        "geojit financial", "stock broking", "brokerage services",
        "wealth management services", "margin trading facility",
    ]),
    ("textiles_apparel", [
        # Was previously falling through to "generic". See
        # textiles_apparel.py docstring. Bare "textiles" is safe here
        # despite sitting after chemicals above — a dyes/pigments chemical
        # company already matches the chemicals rule earlier in this list
        # (first-match-wins), so it never reaches this rule.
        "page industries", "vardhman textiles", "raymond limited", "raymond ltd",
        "arvind limited", "trident limited", "welspun living",
        "textile manufactur", "yarn manufactur", "apparel manufactur",
        "garment manufactur", "textiles",
    ]),
    ("qsr_restaurants", [
        # Was previously falling through to "generic". See
        # qsr_restaurants.py docstring — most listed Indian QSR names are
        # master franchisees, not brand owners, which matters for the
        # royalty/renewal risk framing. "restaurants" is yfinance's own
        # plain industry tag for this group.
        "jubilant foodworks", "devyani international", "sapphire foods",
        "westlife foodworld", "quick service restaurant", "qsr chain",
        "restaurant franchise", "restaurants",
    ]),
    ("retail_apparel", [
        # Was previously falling through to "generic". See
        # retail_apparel.py docstring — must come after consumer_internet
        # above so a pure e-commerce/online retailer isn't reclassified
        # here; this rule targets physical-format apparel/department
        # store retail specifically. "department store retail" is a
        # substring of yfinance's own "Apparel/Department Store Retail" tag.
        "trent limited", "trent ltd", "westside", "zudio",
        "v-mart retail", "shoppers stop", "v2 retail", "aditya birla fashion",
        "department store retail", "apparel retail", "fashion retail chain",
    ]),
]

# ── Compiled patterns ─────────────────────────────────────────────────────────
# \b...\w* allows the keyword to match as a word PREFIX (so "bank" matches
# "Banks", "banking"; "vehicle" matches "vehicles") while still requiring a
# word boundary at the start — this avoids false positives like "vi" matching
# inside "services" (no leading word boundary there) while not breaking on
# ordinary English pluralisation/inflection of our keywords.
_COMPILED: list[tuple[str, list[re.Pattern]]] = [
    (slug, [re.compile(r"\b" + re.escape(kw) + r"\w*", re.IGNORECASE) for kw in kws])
    for slug, kws in _RULES
]


def detect_sector(
    company_name: str = "",
    industry: str = "",
    sector: str = "",
    description: str = "",
    llm_callable=None,          # optional: fn(prompt) -> str
) -> str:
    """
    Returns a sector slug from SECTOR_REGISTRY.

    Parameters
    ----------
    company_name : str  – company display name
    industry     : str  – yfinance info["industry"]
    sector       : str  – yfinance info["sector"]
    description  : str  – longBusinessSummary or Wikipedia extract
    llm_callable : callable or None
        If provided and keyword scan is inconclusive, called as
        ``llm_callable(prompt_str)`` and its return value is parsed for a slug.

    Returns
    -------
    str  – sector slug, e.g. "banking", "it_services", "generic"
    """
    # Two-stage matching: check the authoritative, curated fields (company
    # name, yfinance's own industry/sector classification) BEFORE ever
    # consulting the freeform description. Business descriptions are
    # marketing/overview text that often mentions secondary initiatives
    # (e.g. a legacy oil & gas conglomerate's "New Energy" solar/green-
    # hydrogen division, or a bank's fintech app) — under a single combined
    # first-match-wins scan, an early rule like "renewable_energy" could
    # match on that passing mention and hijack the whole classification
    # even though yfinance's own industry field ("Refiners & Pipelines")
    # already identifies the actual core business unambiguously. Checking
    # the authoritative fields first means a real match there is never
    # overridden by a stray keyword deeper in the description.
    core_haystack = " | ".join(filter(None, [company_name, industry, sector])).lower()
    for slug, patterns in _COMPILED:
        for pat in patterns:
            if pat.search(core_haystack):
                return slug

    # No match on authoritative fields — fall back to scanning the
    # description too (helps for companies with generic/vague industry
    # tags where the description is the only real signal available).
    haystack = " | ".join(filter(None, [
        company_name, industry, sector, description[:500]
    ])).lower()

    for slug, patterns in _COMPILED:
        for pat in patterns:
            if pat.search(haystack):
                return slug

    # LLM fallback
    if llm_callable:
        slug = _llm_detect(llm_callable, company_name, industry, sector, description)
        if slug:
            return slug

    return "generic"


def _llm_detect(llm_fn, company_name, industry, sector, description) -> str:
    """Ask the LLM to classify; extract first valid slug from its reply."""
    from modules.sectors import SECTOR_REGISTRY
    valid_slugs = list(SECTOR_REGISTRY.keys())
    prompt = (
        f"Company: {company_name}\n"
        f"Industry: {industry}\nSector: {sector}\n"
        f"Description: {description[:300]}\n\n"
        f"Classify this company into exactly one of these sector slugs:\n"
        f"{', '.join(valid_slugs)}\n\n"
        "Reply with ONLY the slug. No explanation."
    )
    try:
        reply = llm_fn(prompt).strip().lower()
        for slug in valid_slugs:
            if slug in reply:
                return slug
    except Exception:
        pass
    return ""
