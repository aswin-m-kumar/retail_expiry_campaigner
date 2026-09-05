CREATE TABLE IF NOT EXISTS items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit_cost NUMERIC NOT NULL CHECK (unit_cost > 0),
  mrp NUMERIC NOT NULL CHECK (mrp > 0),
  perishability_tier TEXT NOT NULL CHECK (perishability_tier IN ('high','med','low')),
  CONSTRAINT mrp_covers_cost CHECK (mrp >= unit_cost)
);
