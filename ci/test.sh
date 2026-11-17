#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
REPO=$( cd ${DIR}/.. && pwd )

SPEC=${1:?usage: test.sh <spec> <distro> <app> <arch>}
DISTRO=${2:?distro required}
APP=${3:?app required}
ARCH=${4:?arch required}

DOMAIN="${DISTRO}.com"
APP_DOMAIN="${APP}.${DOMAIN}"
getent hosts ${APP_DOMAIN} | sed "s/${APP_DOMAIN}/auth.${DOMAIN}/g" | tee -a /etc/hosts

APP_ARCHIVE_PATH=$(realpath ${REPO}/$(cat ${REPO}/package.name))

cd ${REPO}/test
./deps.sh
py.test -x -s ${SPEC} --device-user=testuser --distro=${DISTRO} --app-archive-path=${APP_ARCHIVE_PATH} --app=${APP} --arch=${ARCH}
