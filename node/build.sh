#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

VERSION=$1

BUILD_DIR=${DIR}/../build/snap/node

while ! docker ps; do
    echo "waiting for docker"
    sleep 2
done

docker create --name=syncloud rocket.chat:$VERSION
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
docker export syncloud -o syncloud.tar
tar xf syncloud.tar
rm -rf syncloud.tar

echo $VERSION > $BUILD_DIR/rocketchat.version
cp -r ${DIR}/bin ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
