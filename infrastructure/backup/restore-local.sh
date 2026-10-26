#!/usr/bin/env bash
# Replaces the local development database with a production backup, by default
# the newest one pull.sh has copied to this PC. Everything in the local
# database is lost.
#
#   restore-local.sh [backup.dump]
#
# Works on the development stack only (compose.yaml), never on production.
set -euo pipefail

backups="$HOME/Backups/ems"
dump="${1:-}"
if [ -z "$dump" ]; then
    # By time, not by name: the names sort by label first.
    dump=$(find "$backups" -maxdepth 1 -name 'ems-*.dump' -printf '%T@ %p\n' \
        | sort -n | tail -n 1 | cut -d' ' -f2-)
fi
if [ -z "$dump" ] || [ ! -f "$dump" ]; then
    echo "No backup to restore (looked in $backups)" >&2
    exit 1
fi

cd "$(dirname "$0")/.."

compose() {
    docker compose -f compose.yaml "$@"
}

# Runs SQL from stdin in the app database, or in the one given.
psql_in() {
    compose exec -T db sh -c 'psql -X -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "${1:-$POSTGRES_DB}"' sh "${1:-}"
}

echo "==> Restoring $dump"

echo "==> Stopping everything that uses the database"
compose stop server celery-worker celery-beat
compose up -d --wait db

echo "==> Recreating the database"
compose exec -T db sh -c 'psql -X -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres \
    -c "DROP DATABASE IF EXISTS \"$POSTGRES_DB\" WITH (FORCE)" \
    -c "CREATE DATABASE \"$POSTGRES_DB\""'

# TimescaleDB keeps its catalog in ordinary tables, which pg_restore would
# otherwise fill through the extension's own triggers. pre_restore switches
# them off for the database until post_restore.
psql_in <<'SQL'
CREATE EXTENSION timescaledb;
SELECT timescaledb_pre_restore();
SQL

echo "==> Loading the backup"
# Copied in rather than piped: pg_restore cannot always restore from a stream.
compose cp "$dump" db:/tmp/restore.dump
# Production's roles do not exist here; everything is owned by the local user.
compose exec -T db sh -c 'pg_restore --no-owner --no-privileges --exit-on-error \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" /tmp/restore.dump; status=$?; rm -f /tmp/restore.dump; exit $status'

# Production's refresh tokens are signed with its own JWT key and useless here.
psql_in <<'SQL'
SELECT timescaledb_post_restore();
DELETE FROM refresh_tokens;
ANALYZE;
SQL

echo "==> Applying migrations newer than the backup"
compose run --rm --no-deps -T server uv run alembic upgrade head < /dev/null

echo "==> Starting the stack"
compose up -d server celery-worker celery-beat

echo "==> Done"
