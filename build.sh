#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

if [[ -z "$1" ]]; then
    echo "usage $0 app"
    exit 1
fi

NAME=$1
BUILD_DIR=${DIR}/build/${NAME}

apt update
apt -y install python build-essential pkg-config glib2.0-dev libexpat1-dev libtool autoconf

cd $DIR/build
cd vips-*
./configure
make
make install
cp /usr/local/lib/libvips*.so* $BUILD_DIR/nodejs/usr/lib/*-linux-gnu*/
cp /usr/lib/*/libgobject*.so* $BUILD_DIR/nodejs/usr/lib/*-linux-gnu*/

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
#npm install sharp
npm install --unsafe-perm --production
