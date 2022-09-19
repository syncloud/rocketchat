#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

if [[ -z "$1" ]]; then
    echo "usage $0 app"
    exit 1
fi

NAME=$1
ROCKRETCHAT_VERSION=$2
ARCH=$(uname -m)
DOWNLOAD_URL=https://github.com/syncloud/3rdparty/releases/download/
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p $BUILD_DIR

apt update
apt -y install wget

wget https://cdn-download.rocket.chat/build/rocket.chat-$ROCKRETCHAT_VERSION.tgz -O $DIR/node/rocketchat.tar.gz --progress dot:giga
