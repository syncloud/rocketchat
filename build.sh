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
COIN_CACHE_DIR=${DIR}/coin.cache
ARCH=$(uname -m)
SNAP_ARCH=$(dpkg --print-architecture)
VERSION=$2
NODE_VERSION=8.11.3
DOWNLOAD_URL=https://github.com/syncloud/3rdparty/releases/download/1

rm -rf ${DIR}/build
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p ${BUILD_DIR}

cd ${DIR}/build

wget --progress=dot:giga ${DOWNLOAD_URL}/nginx-${ARCH}.tar.gz
tar xf nginx-${ARCH}.tar.gz
mv nginx ${BUILD_DIR}/

wget --progress=dot:giga ${DOWNLOAD_URL}/mongodb-4-${ARCH}.tar.gz
tar xf mongodb-4-${ARCH}.tar.gz
mv mongodb-4 ${BUILD_DIR}/mongodb

wget --progress=dot:giga ${DOWNLOAD_URL}/python-${ARCH}.tar.gz
tar xf python-${ARCH}.tar.gz
mv python ${BUILD_DIR}/

NODE_ARCH=${ARCH}
if [[ ${ARCH} == "x86_64" ]]; then
    NODE_ARCH=x64
fi
NODE_ARCHIVE=node-v${NODE_VERSION}-linux-${NODE_ARCH}
wget https://nodejs.org/dist/v${NODE_VERSION}/${NODE_ARCHIVE}.tar.gz \
    --progress dot:giga
tar xzf ${NODE_ARCHIVE}.tar.gz
mv ${NODE_ARCHIVE} ${BUILD_DIR}/nodejs

mv ${BUILD_DIR}/nodejs/bin/npm ${BUILD_DIR}/nodejs/bin/npm.js
cp ${DIR}/npm/npm ${BUILD_DIR}/nodejs/bin/npm

${BUILD_DIR}/nodejs/bin/npm help

${BUILD_DIR}/python/bin/pip install -r ${DIR}/requirements.txt

${BUILD_DIR}/mongodb/bin/mongod --version

rm -rf ${BUILD_DIR}/lib/node_modules

#export PATH=${BUILD_DIR}/phantomjs/bin:$PATH
#export LD_LIBRARY_PATH=${BUILD_DIR}/phantomjs/lib
#echo "version: \"$(phantomjs --version)\""

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

#cd ${BUILD_DIR}/bundle/programs/server
#git clone git://github.com/Medium/phantomjs.git npm-phantomjs
#cd npm-phantomjs
#git checkout v1.9.20
#cp $DIR/npm/phantomjs/install.js .
#sed -i "s/exports.version.*/exports.version = '1.9.20'/g" lib/phantomjs.js
#${BUILD_DIR}/nodejs/bin/npm install --unsafe-perm --production -g

cd ${BUILD_DIR}/bundle/programs/server
#SHARP_DIST_BASE_URL="http://artifact.syncloud.org/3rdparty/" ${BUILD_DIR}/nodejs/bin/npm install sharp@0.21.0 --unsafe-perm --production -g
#sed -i '/"sharp": "^0.21.0"/d' package.json
#rm -rf npm/node_modules/sharp/vendor
#SHARP_DIST_BASE_URL="http://artifact.syncloud.org/3rdparty/" ${BUILD_DIR}/nodejs/bin/npm install --unsafe-perm --production
${BUILD_DIR}/nodejs/bin/npm install --unsafe-perm --production

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
