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
apt -y install python build-essential pkg-config glib2.0-dev libexpat1-dev

cd $DIR/build
tar xf vips-*
cd vips-*
./configure
make
make install
ldconfig

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
