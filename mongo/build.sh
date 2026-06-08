#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

BUILD_DIR=${DIR}/../build/snap/mongodb

rm -rf ${BUILD_DIR}
mkdir -p ${BUILD_DIR}/bin

cp -r /usr ${BUILD_DIR}/usr
cp -r /lib ${BUILD_DIR}/lib
if [ -d /lib64 ]; then cp -r /lib64 ${BUILD_DIR}/lib64; fi

rm -rf ${BUILD_DIR}/usr/src

cp ${DIR}/bin/* ${BUILD_DIR}/bin

for b in mongos bsondump mongotop mongostat mongoexport mongoimport mongofiles; do
  rm -f ${BUILD_DIR}/usr/bin/$b
done

ls -la ${BUILD_DIR}/bin
${BUILD_DIR}/bin/mongo.sh --help
