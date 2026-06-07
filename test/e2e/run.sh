#!/bin/bash -e
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "${DIR}"

DISTRO="${1:?distro required}"
NAME="${2:?name required}"

export PLAYWRIGHT_FULL_DOMAIN="${DISTRO}.com"
export PLAYWRIGHT_APP_DOMAIN="${NAME}.${DISTRO}.com"
export PLAYWRIGHT_DEVICE_HOST="${NAME}.${DISTRO}.com"
export PLAYWRIGHT_DEVICE_USER="testuser"
export PLAYWRIGHT_DEVICE_PASSWORD="Password1"
export PLAYWRIGHT_ARTIFACT_DIR="/drone/src/artifact/e2e-${DISTRO}"

apt-get update && apt-get install -y sshpass
npm ci
npx playwright test --project=desktop
