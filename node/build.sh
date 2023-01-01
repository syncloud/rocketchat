#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

NODE=$1
ROCKRETCHAT=$2

BUILD_DIR=${DIR}/../build/snap/nodejs

while ! docker ps; do
    echo "waiting for docker"
    sleep 2
done

docker build --build-arg NODE=$NODE -t nodejs:syncloud .
docker run nodejs:syncloud nodejs --help
docker create --name=nodejs nodejs:syncloud
mkdir -p ${BUILD_DIR}
echo $ROCKRETCHAT > $BUILD_DIR/rocketchat.version
cd ${BUILD_DIR}
docker export nodejs -o nodejs.tar
tar xf nodejs.tar
rm -rf nodejs.tar
cp ${DIR}/node.sh ${BUILD_DIR}/bin/

ls -la ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
