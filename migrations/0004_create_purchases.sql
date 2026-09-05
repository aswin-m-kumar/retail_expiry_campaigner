CREATE TABLE IF NOT EXISTS purchases (
  purchase_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
  item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
  purchased_at TIMESTAMPTZ NOT NULL,
  price_paid NUMERIC NOT NULL CHECK (price_paid >= 0),
  discount_applied NUMERIC NOT NULL DEFAULT 0 CHECK (discount_applied BETWEEN 0 AND 100)
);
