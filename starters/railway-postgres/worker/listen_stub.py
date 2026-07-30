#!/usr/bin/env python3
"""Minimal EBFlow LISTEN/NOTIFY stub for Railway Postgres.

Claims pending rows after debounce clears, then hands off to your agent roles.
This is intentionally small: wire ingress / validator / applier yourself.

Env:
  DATABASE_URL   — Railway Postgres URL
  WORKER_ID      — lock owner string (default: worker-local)
  DEBOUNCE_MS    — compare-and-set window (default: 10000)
"""

from __future__ import annotations

import json
import os
import queue
import select
import sys
import time
from datetime import datetime, timedelta, timezone

try:
    import psycopg
except ImportError:
    print("Install psycopg: pip install 'psycopg[binary]'", file=sys.stderr)
    raise


WORKER_ID = os.environ.get("WORKER_ID", "worker-local")
DEBOUNCE_MS = int(os.environ.get("DEBOUNCE_MS", "10000"))


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def claim_pending(conn: psycopg.Connection) -> dict | None:
    """Atomically claim one ready pending row with debounce lock."""
    debounce_until = utcnow() + timedelta(milliseconds=DEBOUNCE_MS)
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH candidate AS (
              SELECT id
              FROM ebflow_requests
              WHERE status = 'pending'
                AND (debounce_until IS NULL OR debounce_until <= now())
              ORDER BY created_at ASC
              FOR UPDATE SKIP LOCKED
              LIMIT 1
            )
            UPDATE ebflow_requests AS r
            SET status = 'processing',
                lock_owner = %s,
                debounce_until = %s,
                attempt_count = attempt_count + 1
            FROM candidate
            WHERE r.id = candidate.id
            RETURNING r.id, r.version, r.idempotency_key, r.payload, r.route, r.target
            """,
            (WORKER_ID, debounce_until),
        )
        row = cur.fetchone()
        conn.commit()
        if not row:
            return None
        keys = ("id", "version", "idempotency_key", "payload", "route", "target")
        return dict(zip(keys, row))


def handle_event(conn: psycopg.Connection, payload: str) -> None:
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        print(f"[warn] bad notify payload: {payload!r}", flush=True)
        return

    print(f"[event] {event}", flush=True)
    claimed = claim_pending(conn)
    if not claimed:
        print("[guard] nothing to claim (debounce, status, or empty queue)", flush=True)
        return

    print(
        f"[claimed] id={claimed['id']} version={claimed['version']} "
        f"→ hand off to validator/applier (stub stops here)",
        flush=True,
    )
    # Next steps in a real worker:
    # 1) route (crud|api)
    # 2) validate idempotently → status=validated + validation_receipt
    # 3) apply → status=applied + apply_receipt
    # 4) main agent completes → status=completed + version++


def drain_notifies(listen_conn: psycopg.Connection, work_conn: psycopg.Connection) -> None:
    """psycopg3 exposes notifies as a queue on the connection."""
    notifies = listen_conn.notifies
    while True:
        try:
            notify = notifies.get_nowait()
        except queue.Empty:
            break
        handle_event(work_conn, notify.payload)


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is required", file=sys.stderr)
        sys.exit(1)

    with psycopg.connect(database_url, autocommit=True) as listen_conn:
        listen_conn.execute("LISTEN ebflow_events")
        print(f"[listen] channel=ebflow_events worker={WORKER_ID}", flush=True)

        with psycopg.connect(database_url) as work_conn:
            work_conn.execute("SELECT set_config('ebflow.actor', 'ingress', false)")
            while True:
                ready, _, _ = select.select([listen_conn.fileno()], [], [], 5.0)
                if ready:
                    # Consume socket data so notifies land on the queue.
                    listen_conn.execute("SELECT 1")
                    drain_notifies(listen_conn, work_conn)
                else:
                    claimed = claim_pending(work_conn)
                    if claimed:
                        print(
                            f"[poll-claim] id={claimed['id']} version={claimed['version']}",
                            flush=True,
                        )
                    else:
                        time.sleep(0.05)


if __name__ == "__main__":
    main()
