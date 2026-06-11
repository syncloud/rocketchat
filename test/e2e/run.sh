#!/bin/bash -e
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "${DIR}"

DISTRO="${1:?distro required}"
NAME="${2:?name required}"
LABEL="${3:?label required}"
TESTDIR="${4:?testdir required}"

export PLAYWRIGHT_FULL_DOMAIN="${DISTRO}.com"
export PLAYWRIGHT_APP_DOMAIN="${NAME}.${DISTRO}.com"
export PLAYWRIGHT_DEVICE_HOST="${NAME}.${DISTRO}.com"
export PLAYWRIGHT_DEVICE_USER="testuser"
export PLAYWRIGHT_DEVICE_PASSWORD="Password1"
export PLAYWRIGHT_SSH_USER="root"
export PLAYWRIGHT_SSH_PASSWORD="Password1"
export PLAYWRIGHT_PROJECT="desktop"
export PLAYWRIGHT_ARTIFACT_DIR="/drone/src/artifact/${LABEL}-${DISTRO}"
export PLAYWRIGHT_TESTDIR="${TESTDIR}"

REPO=$( cd "${DIR}/../.." && pwd )
export PLAYWRIGHT_APP_ARCHIVE="${REPO}/$(cat ${REPO}/package.name)"

apt-get update && apt-get install -y sshpass
npm ci
npx playwright test --project=desktop
