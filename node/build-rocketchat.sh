#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
NAME=rockatchat
ROCKETCHAT_VERSION=1.1.1
BUILD_DIR=${DIR}
mkdir $BUILD_DIR

apt update
apt -y install wget patch libglib2.0-0 python build-essential pkg-config glib2.0-dev libexpat1-dev libtool autoconf g++ build-essential

cd $BUILD_DIR
wget https://github.com/libvips/libvips/releases/download/v8.12.1/vips-8.12.1.tar.gz
tar xf vips-*
rm vips-*.tar.gz
cd vips-*
./configure
make
make install
#cp /usr/local/lib/libvips*.so* $BUILD_DIR/nodejs/usr/lib/*-linux-gnu*/
#ls -la $BUILD_DIR/nodejs/usr/lib/*-linux-gnu*/

cd ${DIR}/build
wget https://cdn-download.rocket.chat/build/rocket.chat-${ROCKETCHAT_VERSION}.tgz -O ${DIR}/build/rocketchat.tar.gz --progress dot:giga
tar xf rocketchat.tar.gz -C ${BUILD_DIR}
cd ${BUILD_DIR}/bundle

for f in ${DIR}/patches/*.patch
do
  patch -p0 < $f
done


ls -la ${BUILD_DIR}
ls -la ${BUILD_DIR}/bundle
chown -R $(whoami). ${BUILD_DIR}/bundle
ls -la ${BUILD_DIR}/bundle
cat ${BUILD_DIR}/bundle/README
ls -la ${BUILD_DIR}/bundle/programs
ls -la ${BUILD_DIR}/bundle/programs/server
export USER=$(whoami)

cd ${BUILD_DIR}/bundle/programs/server
npm install --unsafe-perm --production

mv ${DIR}/bundle ${DIR}/../rocketchat