# modules/sectors/heavy_engineering.py
"""
Heavy Engineering / Equipment Manufacturing — Sector Module
==============================================================
Split out from capital_goods.py: heavy engineering manufacturers (BHEL,
Triveni Turbine, Cummins India, and similar) design and manufacture
large capital equipment (turbines, boilers, diesel/gas engines,
generators) in their own factories, rather than executing site-based EPC
projects (L&T, Thermax) or selling automation software/products (ABB,
Siemens) or branded electrical goods through distribution (Havells,
Polycab). Their economics are driven by manufacturing capacity
utilization, government/public-sector order flow (especially for power
equipment), and — increasingly — export demand, which is a meaningfully
different demand and margin profile from a project-execution contractor
or a branded FMEG distributor.
"""

SECTOR_CONFIG: dict = {
    "slug": "heavy_engineering",
    "display_name": "Heavy Engineering",

    "key_metrics": [
        {"id": "capacity_utilization", "label": "Manufacturing Capacity Utilization", "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "order_book",           "label": "Order Book",                         "unit": "₹Cr", "yf_key": None, "higher_is_better": True},
        {"id": "export_revenue_pct",   "label": "Export Revenue Mix",                 "unit": "%", "yf_key": None, "higher_is_better": True},
        {"id": "government_order_pct", "label": "Government/PSU Order Mix",           "unit": "%", "yf_key": None, "higher_is_better": False},
        {"id": "ebitda_margin",        "label": "EBITDA Margin",                      "unit": "%", "yf_key": "ebitdaMargins", "higher_is_better": True},
        {"id": "roce",                 "label": "Return on Capital Employed",         "unit": "%", "yf_key": "returnOnEquity", "higher_is_better": True},
    ],

    "risk_factors": [
        "Heavy dependence on government/PSU capital equipment orders (especially power equipment) for revenue visibility",
        "Manufacturing capacity underutilization during capex downcycles directly hits margins given high fixed costs",
        "Long manufacturing and delivery lead times create order-to-revenue lag similar to EPC players",
        "Technology transition risk — e.g. thermal power equipment makers face structural demand decline as the energy mix shifts toward renewables",
        "Export competitiveness pressure from lower-cost global manufacturers",
        "Raw material (steel, specialty alloys) cost volatility on largely fixed-price manufacturing contracts",
    ],

    "moat_factors": [
        {"factor": "Manufacturing Scale & Capability", "description": "Heavy capital equipment manufacturing requires large, certified factories that take years and significant capital to replicate"},
        {"factor": "Engineering & Design IP",          "description": "Proprietary turbine/engine/boiler design reduces reliance on licensed foreign technology"},
        {"factor": "PSU/Government Relationships",     "description": "Long-standing qualification and track record with government/PSU buyers is a real barrier for new entrants in that channel"},
        {"factor": "Export Certification & Track Record","description": "Export markets require certifications and a proven reliability track record that take years to build"},
        {"factor": "After-Sales / Spares Annuity",     "description": "Long-life heavy equipment (decades of operating life) generates a recurring spares and service revenue stream"},
    ],

    "bull_case": [
        "Government capex push in power, defence, and railways driving new equipment orders",
        "Export order wins diversifying revenue away from a historically PSU/government-dependent order book",
        "Manufacturing capacity utilization improving as the domestic capex cycle recovers, driving operating leverage",
        "'Make in India' and import-substitution policy tailwinds for domestic heavy-equipment manufacturers",
        "Diversification into new equipment categories (e.g. defence, renewables-adjacent equipment) reducing dependence on legacy thermal/PSU demand",
    ],

    "bear_case": [
        "Structural decline in new thermal power equipment orders as the energy mix shifts toward renewables",
        "Government/PSU capex slowdown or budget delays directly hitting the core order book",
        "Manufacturing capacity underutilization compressing margins given high fixed operating costs",
        "Export competitiveness pressure from lower-cost global manufacturers",
        "Raw material cost spikes eroding margins on largely fixed-price manufacturing contracts",
    ],

    "red_flags": [
        {"condition": "ebitda_margin < 8",  "severity": "high",   "message": "EBITDA margin < 8% — thin for a business with high fixed manufacturing costs, suggests weak capacity utilization"},
        {"condition": "roce < 8",           "severity": "high",   "message": "ROCE < 8% — capital-intensive manufacturing business not clearing a reasonable cost of capital"},
        {"condition": "de_ratio > 1.5",     "severity": "medium", "message": "D/E > 1.5x — high leverage in a cyclical, capital-intensive manufacturing business"},
    ],

    "valuation": {
        "primary":   ["P/E", "EV/EBITDA"],
        "secondary": ["Order Book / Market Cap", "P/E relative to capacity utilization trend"],
        "notes": (
            "Heavy engineering manufacturers are typically valued on P/E relative to their capacity utilization "
            "trend and order book visibility — a recovering utilization rate off a low base can support a "
            "meaningfully higher multiple as operating leverage kicks in. EV/EBITDA is a useful cross-check "
            "given the capital intensity of the manufacturing base."
        ),
        "bands": {
            "pe_ratio": {"attractive": (0, 20), "fair": (20, 35), "expensive": (35, 999)},
        },
    },

    "llm_context": (
        "This is a HEAVY ENGINEERING / EQUIPMENT MANUFACTURING company (e.g. BHEL, Triveni Turbine, Cummins "
        "India) — distinct from an EPC/engineering contractor (L&T, Thermax), which executes site-based "
        "projects rather than manufacturing equipment in its own factories, and distinct from an industrial "
        "automation company (ABB, Siemens), which sells automation software/products rather than heavy "
        "mechanical equipment. Focus on: manufacturing capacity utilization, government/PSU order flow "
        "(especially for legacy thermal power equipment makers, where this is a structural demand headwind), "
        "export revenue mix, and order book visibility. Key demand drivers: government capex (power, defence, "
        "railways), export order wins, capacity utilization recovery. Key risks: structural decline in legacy "
        "thermal power equipment demand as the energy mix shifts toward renewables, government/PSU order "
        "dependence, and capacity underutilization compressing margins given high fixed manufacturing costs. "
        "Do NOT treat this as a pure order-book/execution business like an EPC contractor — capacity "
        "utilization and the government-order dependency (especially any legacy thermal equipment exposure) "
        "are the more important lens here."
    ),
}
