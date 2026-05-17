CREATE TABLE records (
  kind TEXT NOT NULL,
  id TEXT NOT NULL,
  schema TEXT NOT NULL,
  version TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (kind, id)
);
CREATE INDEX idx_records_schema ON records(schema);
CREATE TABLE migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);
INSERT INTO migrations(version, applied_at)
VALUES (1, '2026-05-16T00:00:00+00:00');
PRAGMA user_version = 1;
