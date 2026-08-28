#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_TAG:?IMAGE_TAG is required}"
: "${GHCR_USER:?GHCR_USER is required}"
: "${GHCR_TOKEN:?GHCR_TOKEN is required}"

export IMAGE_TAG
cd /srv/ems

# Because the script arrives on stdin, anything that consumes stdin can truncate
# it. Fail loudly instead of exiting 0 halfway through.
completed=0
trap '[ "$completed" -eq 1 ] || { echo "ERROR: deploy script ended before completing" >&2; exit 1; }' EXIT

compose() {
    docker compose -f compose.prod.yaml "$@"
}

echo "==> Authenticating to ghcr.io"
printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

echo "==> Pulling images for tag ${IMAGE_TAG}"
compose pull --quiet

echo "==> Applying database migrations"
# This script is piped into `bash -s` over SSH, so stdin *is* the script.
# `compose run` attaches stdin to the container by default, which would swallow
# the rest of this file — hence -T and the explicit </dev/null.
compose run --rm -T migrate < /dev/null

echo "==> Starting stack"
compose up -d --remove-orphans

# Compose reads .env from the project directory, so recording the tag here makes
# manual `docker compose` commands on the host default to the deployed version
# instead of :latest. The shell environment still wins during CI runs.
echo "==> Recording deployed tag"
if grep -q '^IMAGE_TAG=' .env; then
    sed -i "s|^IMAGE_TAG=.*|IMAGE_TAG=${IMAGE_TAG}|" .env
else
    printf 'IMAGE_TAG=%s\n' "$IMAGE_TAG" >> .env
fi

echo "==> Reclaiming disk from superseded images"
docker image prune --force

echo "==> Done"
compose ps

completed=1
