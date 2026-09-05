CREATE TABLE IF NOT EXISTS notifications (
  notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
  inventory_id UUID NOT NULL REFERENCES inventory(inventory_id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  reasoning_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
