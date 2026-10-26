#!/usr/bin/env bash
# Copies the database backups from the server to this PC, the copy that
# survives losing the server. Run by ems-backup-pull.timer.
#
# Keeps far more than the server does: a bug that quietly damages the data may
# go unnoticed for longer than the server's three days.
set -euo pipefail

source=lilian@lilianluca.com:/srv/ems/backups/
dest="$HOME/Backups/ems"

mkdir -p "$dest"
chmod 700 "$dest"

# No --delete: what the server rotates out stays here. Only finished dumps;
# the hidden .partial files are still being written. Times but not owners: the
# deploy group does not exist on this PC.
rsync -rt -e "ssh -o BatchMode=yes" \
    --include='ems-*.dump' --exclude='*' \
    "$source" "$dest/"

# Rotate by count rather than age, as on the server. Both keep more than the
# server, so nothing removed here is ever pulled again.
rotate() {
    local label="$1" keep="$2"
    find "$dest" -maxdepth 1 -name "ems-${label}-*.dump" -printf '%f\n' \
        | sort \
        | head -n -"$keep" \
        | while read -r old; do
            rm -- "$dest/$old"
            echo "Removed $old"
        done
}
# About 30 days of three backups a day.
rotate scheduled 90
rotate pre-deploy 10

echo "Newest: $(find "$dest" -maxdepth 1 -name 'ems-*.dump' -printf '%f\n' | sort | tail -n 1)"
