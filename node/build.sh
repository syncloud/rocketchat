#!/bin/bash -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

VERSION=$1

BUILD_DIR=${DIR}/../build/snap/node

mkdir -p ${BUILD_DIR}
cp -r /app/bundle $BUILD_DIR/rocketchat
echo $VERSION > $BUILD_DIR/rocketchat.version
cp -r /usr ${BUILD_DIR}
cp -r /lib ${BUILD_DIR}
cp -r ${DIR}/bin ${BUILD_DIR}/bin
