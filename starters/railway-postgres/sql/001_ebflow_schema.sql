-- EBFlow Postgres schema (Railway-friendly)
-- Aligns with schemas/request.schema.json, schemas/history.schema.json,
-- schemas/status.schema.json, and skills/ebflow/status-machine.md

BEGIN;

CREATE TYPE ebflow_status AS ENUM (
  'pending',
  'processing',
  'validated',
  'applied',
  'completed',
  'failed',
  'escalated'
);

CREATE TYPE ebflow_route AS ENUM ('crud', 'api');

CREATE TYPE ebflow_actor AS ENUM (
  'entry',
  'ingress',
  'validator',
  'applier',
  'main_agent',
  'human'
);

CREATE TYPE ebflow_failure_stage AS ENUM (
  'ingress',
  'route',
  'validate',
  'apply',
  'complete'
);

CREATE TABLE ebflow_requests (
  id                  text PRIMARY KEY,
  idempotency_key     text NOT NULL,
  version             integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  status              ebflow_status NOT NULL DEFAULT 'pending',
  route               ebflow_route,
  target              text,
  payload             jsonb NOT NULL DEFAULT '{}'::jsonb,
  validation_receipt  jsonb,
  apply_receipt       jsonb,
  failure             jsonb,
  attempt_count       integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
  next_retry_at       timestamptz,
  debounce_until      timestamptz,
  lock_owner          text,
  context_path        text,
  history_id          text,
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ebflow_requests_idempotency_unique UNIQUE (idempotency_key),
  CONSTRAINT ebflow_requests_failure_shape CHECK (
    failure IS NULL OR (
      failure ? 'code'
      AND failure ? 'message'
      AND failure ? 'stage'
      AND failure ? 'transient'
      AND failure ? 'at'
    )
  )
);

CREATE INDEX ebflow_requests_status_updated_idx
  ON ebflow_requests (status, updated_at);

CREATE INDEX ebflow_requests_pending_ready_idx
  ON ebflow_requests (created_at)
  WHERE status = 'pending'
    AND (debounce_until IS NULL OR debounce_until <= now());

CREATE INDEX ebflow_requests_retry_ready_idx
  ON ebflow_requests (next_retry_at)
  WHERE status = 'failed'
    AND next_retry_at IS NOT NULL;

CREATE TABLE ebflow_history (
  id               text PRIMARY KEY,
  request_id       text NOT NULL REFERENCES ebflow_requests (id) ON DELETE CASCADE,
  version          integer NOT NULL CHECK (version >= 1),
  idempotency_key  text,
  route            ebflow_route,
  target           text,
  summary          text NOT NULL,
  why              text NOT NULL,
  result           text NOT NULL,
  failures         jsonb NOT NULL DEFAULT '[]'::jsonb,
  context_path     text NOT NULL,
  created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ebflow_history_request_idx
  ON ebflow_history (request_id, version DESC);

CREATE TABLE ebflow_status_transitions (
  id          bigserial PRIMARY KEY,
  request_id  text NOT NULL REFERENCES ebflow_requests (id) ON DELETE CASCADE,
  version     integer NOT NULL CHECK (version >= 1),
  from_status ebflow_status NOT NULL,
  to_status   ebflow_status NOT NULL,
  actor       ebflow_actor NOT NULL,
  reason      text,
  at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ebflow_status_transitions_request_idx
  ON ebflow_status_transitions (request_id, at DESC);

-- Legal transitions (see skills/ebflow/status-machine.md)
CREATE OR REPLACE FUNCTION ebflow_transition_allowed(
  from_status ebflow_status,
  to_status ebflow_status
) RETURNS boolean
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT CASE
    WHEN from_status = 'pending'     AND to_status = 'processing' THEN true
    WHEN from_status = 'processing'  AND to_status IN ('validated', 'failed') THEN true
    WHEN from_status = 'validated'   AND to_status IN ('applied', 'failed') THEN true
    WHEN from_status = 'applied'     AND to_status IN ('completed', 'failed') THEN true
    WHEN from_status = 'failed'      AND to_status IN ('processing', 'escalated') THEN true
    WHEN from_status = 'escalated'   AND to_status IN ('processing', 'pending') THEN true
    ELSE false
  END;
$$;

CREATE OR REPLACE FUNCTION ebflow_requests_before_update()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.status IS DISTINCT FROM OLD.status THEN
    IF NOT ebflow_transition_allowed(OLD.status, NEW.status) THEN
      RAISE EXCEPTION 'illegal ebflow transition: % → % (request %)',
        OLD.status, NEW.status, OLD.id;
    END IF;

    -- Only main-agent completion should bump version (recommended policy).
    IF NEW.status = 'completed' AND NEW.version <= OLD.version THEN
      RAISE EXCEPTION 'completed requires version bump (request %): old=% new=%',
        OLD.id, OLD.version, NEW.version;
    END IF;

    INSERT INTO ebflow_status_transitions (
      request_id, version, from_status, to_status, actor, reason, at
    ) VALUES (
      NEW.id,
      NEW.version,
      OLD.status,
      NEW.status,
      COALESCE(NULLIF(current_setting('ebflow.actor', true), '')::ebflow_actor, 'ingress'),
      NULLIF(current_setting('ebflow.reason', true), ''),
      now()
    );
  END IF;

  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_ebflow_requests_before_update
BEFORE UPDATE ON ebflow_requests
FOR EACH ROW
EXECUTE PROCEDURE ebflow_requests_before_update();

-- Optional: LISTEN/NOTIFY wake for pending inserts / status changes.
-- Worker stub: LISTEN ebflow_events; then claim rows by status.
CREATE OR REPLACE FUNCTION ebflow_notify_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  payload text;
BEGIN
  payload := json_build_object(
    'id', NEW.id,
    'status', NEW.status,
    'version', NEW.version,
    'idempotency_key', NEW.idempotency_key,
    'op', TG_OP
  )::text;

  PERFORM pg_notify('ebflow_events', payload);
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_ebflow_requests_notify
AFTER INSERT OR UPDATE OF status, version, debounce_until ON ebflow_requests
FOR EACH ROW
EXECUTE PROCEDURE ebflow_notify_change();

COMMENT ON TABLE ebflow_requests IS
  'EBFlow durable request row. Source of truth for status/version.';
COMMENT ON COLUMN ebflow_requests.debounce_until IS
  'If now < debounce_until, workers ack and stop (event storm absorption).';
COMMENT ON COLUMN ebflow_requests.idempotency_key IS
  'Stable for user intent. Retries keep the same key; new intents get a new key.';
COMMENT ON TRIGGER trg_ebflow_requests_notify ON ebflow_requests IS
  'Fires pg_notify on channel ebflow_events. Prefer LISTEN in a worker, or mirror via webhook from your app layer.';

COMMIT;
