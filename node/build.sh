#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
apt update
apt install -y libltdl7 libnss3

wget https://github.com/libvips/libvips/releases/download/v8.12.1/vips-8.12.1.tar.gz --progress dot:giga
wget https://cdn-download.rocket.chat/build/rocket.chat-${2}.tgz -O rocketchat.tar.gz --progress dot:giga

BUILD_DIR=${DIR}/../build/rocketchat/nodejs
docker ps -a -q --filter ancestor=nodejs:syncloud --format="{{.ID}}" | xargs docker stop | xargs docker rm || true
docker rmi nodejs:syncloud || true
docker build --build-arg NODE_VERSION=$1 -t nodejs:syncloud .
docker run nodejs:syncloud nodejs --help
docker create --name=nodejs nodejs:syncloud
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
docker export nodejs -o nodejs.tar
docker ps -a -q --filter ancestor=nodejs:syncloud --format="{{.ID}}" | xargs docker stop | xargs docker rm || true
docker rmi nodejs:syncloud || true
tar xf nodejs.tar
rm -rf nodejs.tar
cp ${DIR}/node.sh ${BUILD_DIR}/bin/
${BUILD_DIR}/bin/node.sh --help
ls -la ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
