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
ROCKETCHAT_VERSION=0.60.2
COIN_CACHE_DIR=${DIR}/coin.cache
ARCH=$(uname -m)
SNAP_ARCH=$(dpkg --print-architecture)
VERSION=$2
INSTALLER=$3

apt-get update
apt-get -y install git

rm -rf ${DIR}/lib
mkdir ${DIR}/lib

#coin --to lib py https://pypi.python.org/packages/2.7/b/beautifulsoup4/beautifulsoup4-4.4.0-py2-none-any.whl
#coin --to lib py https://pypi.python.org/packages/ea/03/92d3278bf8287c5caa07dbd9ea139027d5a3592b0f4d14abf072f890fab2/requests-2.11.1-py2.py3-none-any.whl#md5=b4269c6fb64b9361288620ba028fd385
#coin --to lib py https://pypi.python.org/packages/f3/94/67d781fb32afbee0fffa0ad9e16ad0491f1a9c303e14790ae4e18f11be19/requests-unixsocket-0.1.5.tar.gz#md5=08453c8ef7dc03863ff4a30b901e7c20
#coin --to lib py https://pypi.python.org/packages/source/m/massedit/massedit-0.67.1.zip
#coin --to lib py https://pypi.python.org/packages/df/5e/afeef90d3f90521a5422053892a4f44c1451f1584053f9669705ab98dd43/syncloud-lib-28.tar.gz#md5=10c8347b0a15d760da39b56d91d5a11e

if [ $SNAP_ARCH == "armhf" ]; then
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

#wget $SRC_SNAP_URL --progress dot:giga
#unsquashfs -d ${DIR}/build/src_snap $SRC_SNAP
#ls -la ${DIR}/build/src_snap/
#ls -la ${DIR}/build/src_snap/bin

#mkdir ${BUILD_DIR}/mongodb
#mkdir ${BUILD_DIR}/mongodb/bin
#mkdir ${BUILD_DIR}/mongodb/lib

#cp ${DIR}/bin/mongod ${BUILD_DIR}/mongodb/bin/
#cp ${DIR}/build/src_snap/usr/bin/mongod ${BUILD_DIR}/mongodb/bin/mongod.bin || true
#cp ${DIR}/build/src_snap/bin/mongod ${BUILD_DIR}/mongodb/bin/mongod.bin || true

#cp -r -L ${DIR}/build/src_snap/lib/$(dpkg-architecture -q DEB_HOST_GNU_TYPE)/* ${BUILD_DIR}/mongodb/lib/
#cp -r -L ${DIR}/build/src_snap/usr/lib/$(dpkg-architecture -q DEB_HOST_GNU_TYPE)/* ${BUILD_DIR}/mongodb/lib/
#cp -r -L ${DIR}/build/src_snap/usr/lib/* ${BUILD_DIR}/mongodb/lib/

coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/nodejs-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/nginx-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/mongodb-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/phantomjs-${ARCH}.tar.gz

${BUILD_DIR}/mongodb/bin/mongod --version

rm /usr/bin/phantomjs
rm -rf ${BUILD_DIR}/lib/node_modules

#${BUILD_DIR}/nodejs/bin/npm install phantomjs@1.9.20 || true

export PATH=${BUILD_DIR}/phantomjs/bin:$PATH
export LD_LIBRARY_PATH=${BUILD_DIR}/phantomjs/lib
echo "version: \"$(phantomjs --version)\""

cd ${DIR}/build
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

git clone git://github.com/Medium/phantomjs.git npm-phantomjs
cd npm-phantomjs
git checkout v1.9.20
cp $DIR/npm/phantomjs/install.js .
sed -i "s/exports.version.*/exports.version = '1.9.20'/g" lib/phantomjs.js
${BUILD_DIR}/nodejs/bin/npm install --unsafe-perm --production -g
#${BUILD_DIR}/nodejs/bin/node ./install.js
cd ..
#mv npm-phantomjs/node_modules .
export USER=$(whoami)
${BUILD_DIR}/nodejs/bin/npm install --unsafe-perm --verbose --production

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