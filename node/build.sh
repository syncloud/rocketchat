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

echo $VERSION > rocketchat.version
cp ${DIR}/bin/* bin
rm -rf /usr/src
