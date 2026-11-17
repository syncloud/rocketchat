#!/bin/bash -e
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "${DIR}"

SPEC=${1:?usage: run.sh <spec>}
LABEL=$(basename "${SPEC}" .spec.ts)

REPO=$( cd "${DIR}/../.." && pwd )

export PLAYWRIGHT_FULL_DOMAIN=bookworm.com
export PLAYWRIGHT_APP_DOMAIN=rocketchat.bookworm.com
export PLAYWRIGHT_DEVICE_HOST=rocketchat.bookworm.com
export PLAYWRIGHT_DEVICE_USER=testuser
export PLAYWRIGHT_DEVICE_PASSWORD=Password1
export PLAYWRIGHT_SSH_USER=root
export PLAYWRIGHT_SSH_PASSWORD=Password1
export PLAYWRIGHT_PROJECT=desktop
export PLAYWRIGHT_ARTIFACT_DIR=${REPO}/artifact/screenshots
export PLAYWRIGHT_LOG_DIR=${REPO}/artifact/e2e-log/${LABEL}

${REPO}/apt.sh sshpass openssh-client curl
${DIR}/wait-app.sh ${PLAYWRIGHT_APP_DOMAIN}
${REPO}/retry.sh npm ci --no-audit --no-fund
npx playwright test --project=${PLAYWRIGHT_PROJECT} "${SPEC}"
