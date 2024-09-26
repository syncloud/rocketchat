#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

BUILD_DIR=${DIR}/../build/snap/mongodb
docker build --build-arg MONGO=$1 -t mongo:syncloud .
docker run mongo:syncloud mongosh --help
docker create --name=mongo mongo:syncloud
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
docker export mongo -o mongo.tar
tar xf mongo.tar
rm -rf mongo.tar
cp ${DIR}/bin/* ${BUILD_DIR}/bin
ls -la ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
rm ${BUILD_DIR}/usr/bin/mongos
#rm ${BUILD_DIR}/usr/bin/mongosh
rm ${BUILD_DIR}/usr/bin/bsondump
rm ${BUILD_DIR}/usr/bin/mongotop
rm ${BUILD_DIR}/usr/bin/mongostat
rm ${BUILD_DIR}/usr/bin/mongoexport
rm ${BUILD_DIR}/usr/bin/mongoimport
rm ${BUILD_DIR}/usr/bin/mongofiles
