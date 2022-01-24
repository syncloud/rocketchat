#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
apt update
apt install -y libltdl7 libnss3

BUILD_DIR=${DIR}/../build/rocketchat/mongodb
docker ps -a -q --filter ancestor=mongo:syncloud --format="{{.ID}}" | xargs docker stop | xargs docker rm || true
docker rmi mongo:syncloud || true
docker build -t mongo:syncloud .
docker run mongo:syncloud mongo --help
docker create --name=mongo mongo:syncloud
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
docker export mongo -o mongo.tar
docker ps -a -q --filter ancestor=mongo:syncloud --format="{{.ID}}" | xargs docker stop | xargs docker rm || true
docker rmi mongo:syncloud || true
tar xf mongo.tar
rm -rf mongo.tar
cp ${DIR}/mongod.sh ${BUILD_DIR}/bin/
cp ${DIR}/mongo.sh ${BUILD_DIR}/bin/
ls -la ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
