#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

VERSION=$1

BUILD_DIR=${DIR}/../build/snap/node

rm -rf ${BUILD_DIR}
mkdir -p ${BUILD_DIR}/bin

cp -r /app ${BUILD_DIR}/app
cp -r /usr ${BUILD_DIR}/usr
cp -r /lib ${BUILD_DIR}/lib
if [ -d /lib64 ]; then cp -r /lib64 ${BUILD_DIR}/lib64; fi

rm -rf ${BUILD_DIR}/usr/src

cp ${DIR}/bin/* ${BUILD_DIR}/bin

echo $VERSION > ${BUILD_DIR}/rocketchat.version

${BUILD_DIR}/bin/node.sh --version
