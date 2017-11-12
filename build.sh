#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

if [[ -z "$3" ]]; then
    echo "usage $0 app version installer"
    exit 1
fi

export TMPDIR=/tmp
export TMP=/tmp

NAME=$1
ROCKETCHAT_VERSION=0.59.3
COIN_CACHE_DIR=${DIR}/coin.cache
ARCH=$(uname -m)
SNAP_ARCH=$(dpkg --print-architecture)
VERSION=$2
INSTALLER=$3

rm -rf ${DIR}/lib
mkdir ${DIR}/lib

#coin --to lib py https://pypi.python.org/packages/2.7/b/beautifulsoup4/beautifulsoup4-4.4.0-py2-none-any.whl
#coin --to lib py https://pypi.python.org/packages/ea/03/92d3278bf8287c5caa07dbd9ea139027d5a3592b0f4d14abf072f890fab2/requests-2.11.1-py2.py3-none-any.whl#md5=b4269c6fb64b9361288620ba028fd385
#coin --to lib py https://pypi.python.org/packages/f3/94/67d781fb32afbee0fffa0ad9e16ad0491f1a9c303e14790ae4e18f11be19/requests-unixsocket-0.1.5.tar.gz#md5=08453c8ef7dc03863ff4a30b901e7c20
#coin --to lib py https://pypi.python.org/packages/source/m/massedit/massedit-0.67.1.zip
#coin --to lib py https://pypi.python.org/packages/source/s/syncloud-lib/syncloud-lib-2.tar.gz

if [ $SNAP_ARCH == "armhf ]; then
    SRC_SNAP_BUILD=22904
else
    SRC_SNAP_BUILD=22903
fi

SRC_SNAP=rocketchat-server_0.52.0_$SNAP_ARCH.snap
SRC_SNAP_URL=https://code.launchpad.net/~sing-li/+snap/rocketchat-server/+build/$SRC_SNAP_BUILD/+files/$SRC_SNAP
DOWNLOAD_URL=http://artifact.syncloud.org/3rdparty

rm -rf ${DIR}/build
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p ${BUILD_DIR}

cd ${DIR}/build

wget $SRC_SNAP_URL
unsquashfs -d ${DIR}/build/src_snap $SRC_SNAP

ls -la ${DIR}/build/src_snap/
ls -la ${DIR}/build/src_snap/bin

mkdir ${BUILD_DIR}/mongodb
mkdir ${BUILD_DIR}/mongodb/bin

cp ${DIR}/build/src_snap/bin/mongod ${BUILD_DIR}/mongodb/bin/

coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/nodejs-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/nginx-${ARCH}.tar.gz
#coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/mongodb-${ARCH}.tar.gz

wget https://download.rocket.chat/build/rocket.chat-${ROCKETCHAT_VERSION}.tgz -O ${DIR}/build/rocketchat.tar.gz --progress dot:giga

tar xf rocketchat.tar.gz -C ${BUILD_DIR}

cp -r ${DIR}/bin ${BUILD_DIR}
cp -r ${DIR}/config ${BUILD_DIR}/config.templates
cp -r ${DIR}/lib ${BUILD_DIR}
cp -r ${DIR}/hooks ${BUILD_DIR}

ls -la ${BUILD_DIR}
ls -la ${BUILD_DIR}/bundle
chown -R $(whoami). ${BUILD_DIR}/bundle
ls -la ${BUILD_DIR}/bundle
cat ${BUILD_DIR}/bundle/README
ls -la ${BUILD_DIR}/bundle/programs
ls -la ${BUILD_DIR}/bundle/programs/server

cd ${BUILD_DIR}/bundle/programs/server
export USER=$(whoami)
rm /usr/bin/phantomjs
${BUILD_DIR}/nodejs/bin/npm install --unsafe-perm

mkdir ${DIR}/build/${NAME}/META
echo ${NAME} >> ${DIR}/build/${NAME}/META/app
echo ${VERSION} >> ${DIR}/build/${NAME}/META/version

if [ $INSTALLER == "sam" ]; then

    echo "zipping"
    rm -rf ${NAME}*.tar.gz
    tar cpzf ${DIR}/${NAME}-${VERSION}-${ARCH}.tar.gz -C ${DIR}/build/ ${NAME}

else

    echo "snapping"
    SNAP_DIR=${DIR}/build/snap
    ARCH=$(dpkg-architecture -q DEB_HOST_ARCH)
    rm -rf ${DIR}/*.snap
    mkdir ${SNAP_DIR}
    cp -r ${BUILD_DIR}/* ${SNAP_DIR}/
    cp -r ${DIR}/snap/meta ${SNAP_DIR}/
    cp ${DIR}/snap/snap.yaml ${SNAP_DIR}/meta/snap.yaml
    echo "version: $VERSION" >> ${SNAP_DIR}/meta/snap.yaml
    echo "architectures:" >> ${SNAP_DIR}/meta/snap.yaml
    echo "- ${ARCH}" >> ${SNAP_DIR}/meta/snap.yaml

    mksquashfs ${SNAP_DIR} ${DIR}/${NAME}_${VERSION}_${ARCH}.snap -noappend -comp xz -no-xattrs -all-root

fi