#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}
apt install -y libltdl7 libnss3

NODE=$1
ROCKRETCHAT=$2

BUILD_DIR=${DIR}/../build/snap/nodejs

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
${BUILD_DIR}/bin/node.sh --help
ls -la ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
