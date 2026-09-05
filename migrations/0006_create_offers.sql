CREATE TABLE IF NOT EXISTS offers (
  offer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
  inventory_id UUID NOT NULL REFERENCES inventory(inventory_id) ON DELETE CASCADE,
  strategy_type TEXT NOT NULL CHECK (strategy_type IN ('small_perk','tiered_discount','aggressive_discount')),
  discount_pct NUMERIC NOT NULL CHECK (discount_pct BETWEEN 0 AND 100),
  reasoning_text TEXT NOT NULL,
  urgency_score NUMERIC NOT NULL CHECK (urgency_score BETWEEN 0 AND 1),
  affinity_score NUMERIC NOT NULL CHECK (affinity_score BETWEEN 0 AND 1),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
