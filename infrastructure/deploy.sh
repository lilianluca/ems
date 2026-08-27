#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_TAG:?IMAGE_TAG is required}"
: "${GHCR_USER:?GHCR_USER is required}"
: "${GHCR_TOKEN:?GHCR_TOKEN is required}"

export IMAGE_TAG
cd /srv/ems

compose() {
    docker compose -f compose.prod.yaml "$@"
}

echo "==> Authenticating to ghcr.io"
printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

echo "==> Pulling images for tag ${IMAGE_TAG}"
compose pull --quiet

echo "==> Applying database migrations"
compose run --rm migrate

echo "==> Starting stack"
compose up -d --remove-orphans

echo "==> Reclaiming disk from superseded images"
docker image prune --force

echo "==> Done"
compose ps
