#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

if [[ -z "$1" ]]; then
    echo "usage $0 app"
    exit 1
fi

NAME=$1
ARCH=$(uname -m)
DOWNLOAD_URL=https://github.com/syncloud/3rdparty/releases/download/
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p $BUILD_DIR

apt update
apt -y install wget

cd ${DIR}/build
wget -c --progress=dot:giga ${DOWNLOAD_URL}/nginx/nginx-${ARCH}.tar.gz
tar xf nginx-${ARCH}.tar.gz
mv nginx ${BUILD_DIR}/
