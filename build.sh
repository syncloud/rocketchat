#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

if [[ -z "$2" ]]; then
    echo "usage $0 app version"
    exit 1
fi

export TMPDIR=/tmp
export TMP=/tmp

NAME=$1
ROCKETCHAT_VERSION=3.9.0
#COIN_CACHE_DIR=${DIR}/coin.cache
ARCH=$(uname -m)
#SNAP_ARCH=$(dpkg --print-architecture)
VERSION=$2
#NODE_VERSION=12.18.4
DOWNLOAD_URL=https://github.com/syncloud/3rdparty/releases/download/

BUILD_DIR=${DIR}/build/${NAME}

cd ${DIR}/build

wget -c --progress=dot:giga ${DOWNLOAD_URL}/nginx/nginx-${ARCH}.tar.gz
tar xf nginx-${ARCH}.tar.gz
mv nginx ${BUILD_DIR}/

#NODE_ARCH=${ARCH}
#if [[ ${ARCH} == "x86_64" ]]; then
#    NODE_ARCH=x64
#fi
#NODE_ARCHIVE=node-v${NODE_VERSION}-linux-${NODE_ARCH}
#wget https://nodejs.org/dist/v${NODE_VERSION}/${NODE_ARCHIVE}.tar.gz \
#    --progress dot:giga
#tar xzf ${NODE_ARCHIVE}.tar.gz
#mv ${NODE_ARCHIVE} ${BUILD_DIR}/nodejs

#mv ${BUILD_DIR}/nodejs/bin/npm ${BUILD_DIR}/nodejs/bin/npm.js
#cp ${DIR}/npm/npm ${BUILD_DIR}/nodejs/bin/npm

${BUILD_DIR}/nodejs/bin/npm help

${BUILD_DIR}/mongodb/bin/mongod.sh --version
${BUILD_DIR}/mongodb/bin/mongo.sh --version

rm -rf ${BUILD_DIR}/lib/node_modules

cd ${DIR}/build
wget https://cdn-download.rocket.chat/build/rocket.chat-${ROCKETCHAT_VERSION}.tgz -O ${DIR}/build/rocketchat.tar.gz --progress dot:giga
tar xf rocketchat.tar.gz -C ${BUILD_DIR}
cd ${BUILD_DIR}/bundle

for f in ${DIR}/patches/*.patch
do
  patch -p0 < $f
done

cd ${DIR}
cp -r ${DIR}/bin ${BUILD_DIR}
cp -r ${DIR}/config ${BUILD_DIR}/config.templates
cp -r ${DIR}/hooks ${BUILD_DIR}

ls -la ${BUILD_DIR}
ls -la ${BUILD_DIR}/bundle
chown -R $(whoami). ${BUILD_DIR}/bundle
ls -la ${BUILD_DIR}/bundle
cat ${BUILD_DIR}/bundle/README
ls -la ${BUILD_DIR}/bundle/programs
ls -la ${BUILD_DIR}/bundle/programs/server
export USER=$(whoami)

cd ${BUILD_DIR}/bundle/programs/server
${BUILD_DIR}/nodejs/usr/local/bin/npm install --unsafe-perm --production

mkdir ${DIR}/build/${NAME}/META
echo ${NAME} >> ${DIR}/build/${NAME}/META/app
echo ${VERSION} >> ${DIR}/build/${NAME}/META/version

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

PACKAGE=${NAME}_${VERSION}_${ARCH}.snap
echo ${PACKAGE} > ${DIR}/package.name
mksquashfs ${SNAP_DIR} ${DIR}/${PACKAGE} -noappend -comp xz -no-xattrs -all-root
