#!/usr/bin/env bash
# Dumps the production database into /srv/ems/backups and keeps the newest few.
#
#   backup.sh scheduled    from ems-backup.timer, three times a day
#   backup.sh pre-deploy   from deploy.sh, before the migrations
#
# Each label is rotated on its own, so a run of deploys never pushes out the
# scheduled backups. Runs as `deploy`, the only user that can read .env.
set -euo pipefail

label="${1:-}"
case "$label" in
    scheduled) keep=9 ;;
    pre-deploy) keep=3 ;;
    *)
        echo "usage: backup.sh scheduled|pre-deploy" >&2
        exit 2
        ;;
esac

cd /srv/ems
backup_dir=/srv/ems/backups

# The dumps hold password hashes and refresh tokens: readable by the deploy
# group, which the user pulling them to the PC belongs to, and nobody else.
umask 027
mkdir -p "$backup_dir"

compose() {
    docker compose -f compose.prod.yaml "$@"
}

name="ems-${label}-$(date -u +%Y%m%dT%H%M%SZ).dump"
# Hidden and suffixed until it is verified, so neither the rotation below nor
# the pull to the PC ever takes a half-written dump for a backup.
partial="$backup_dir/.${name}.partial"
trap 'rm -f "$partial"' EXIT

# Custom format: compressed, and restorable table by table with pg_restore.
# </dev/null because deploy.sh runs from stdin, which exec would consume.
compose exec -T db sh -c 'pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
    < /dev/null > "$partial"

# Reads the whole archive, not just its table of contents (`pg_restore -l`
# passes a truncated file), and throws the resulting SQL away.
compose exec -T db pg_restore -f /dev/null < "$partial"

mv "$partial" "$backup_dir/$name"
echo "Backed up to $backup_dir/$name ($(du -h "$backup_dir/$name" | cut -f1))"

# Rotate by count rather than age: if backups stop working, the old ones stay.
# The names sort by time, newest last.
find "$backup_dir" -maxdepth 1 -name "ems-${label}-*.dump" -printf '%f\n' \
    | sort \
    | head -n -"$keep" \
    | while read -r old; do
        rm -- "$backup_dir/$old"
        echo "Removed $old"
    done
