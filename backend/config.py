import os

# Inventory scanned if days_to_expiry <= this
EXPIRY_WINDOW_DAYS = 30

# Per perishability_tier multiplier (high, med, low)
URGENCY_WEIGHTS = {
    "high": 1.5,
    "med": 1.0,
    "low": 0.5
}

# Purchase history window for affinity calculation
AFFINITY_LOOKBACK_DAYS = 90

# Mapping strategy_type -> (min_pct, max_pct)
DISCOUNT_BANDS = {
    "small_perk": (5, 15),
    "tiered_discount": (16, 30),
    "aggressive_discount": (31, 50)
}

# Score above which -> notify only (won't buy anyway)
WOULD_BUY_ANYWAY_THRESHOLD = 0.7
