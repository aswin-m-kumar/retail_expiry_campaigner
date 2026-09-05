CREATE TABLE IF NOT EXISTS inventory (
  inventory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
  batch_no TEXT NOT NULL,
  stock_qty INT NOT NULL CHECK (stock_qty >= 0),
  expiry_date DATE NOT NULL
);
