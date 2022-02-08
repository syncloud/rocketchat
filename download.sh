#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

if [[ -z "$1" ]]; then
    echo "usage $0 app"
    exit 1
fi

NAME=$1
ROCKETCHAT_VERSION=1.3.1
ARCH=$(uname -m)
DOWNLOAD_URL=https://github.com/syncloud/3rdparty/releases/download/
BUILD_DIR=${DIR}/build/${NAME}

cd ${DIR}/build

apt update
apt -y install wget patch

wget -c --progress=dot:giga ${DOWNLOAD_URL}/nginx/nginx-${ARCH}.tar.gz
tar xf nginx-${ARCH}.tar.gz
mv nginx ${BUILD_DIR}/

wget https://github.com/libvips/libvips/releases/download/v8.12.1/vips-8.12.1.tar.gz
tar xf vips-*
rm vips-*.tar.gz

cd ${DIR}/build
wget https://cdn-download.rocket.chat/build/rocket.chat-${ROCKETCHAT_VERSION}.tgz -O ${DIR}/build/rocketchat.tar.gz --progress dot:giga
tar xf rocketchat.tar.gz -C ${BUILD_DIR}
cd ${BUILD_DIR}/bundle

for f in ${DIR}/patches/*.patch
do
  patch -p0 < $f
done
