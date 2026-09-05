CREATE TABLE IF NOT EXISTS "user" (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('customer','owner')),
  join_date DATE NOT NULL,
  visit_frequency_per_month NUMERIC NOT NULL CHECK (visit_frequency_per_month >= 0),
  loyalty_tier TEXT NOT NULL CHECK (loyalty_tier IN ('new','regular','vip')),
  avg_basket_value NUMERIC NOT NULL CHECK (avg_basket_value >= 0),
  discount_sensitivity TEXT NOT NULL CHECK (discount_sensitivity IN ('responsive','neutral','insensitive'))
);
