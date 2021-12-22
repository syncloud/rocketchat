#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
apt update
apt install -y libltdl7 libnss3

BUILD_DIR=${DIR}/../build/rocketchat/nodejs
docker ps -a -q --filter ancestor=nodejs:syncloud --format="{{.ID}}" | xargs docker stop | xargs docker rm || true
docker rmi nodejs:syncloud || true
docker build -t nodejs:syncloud .
docker run nodejs:syncloud nodejs --help
docker create --name=nodejs nodejs:syncloud
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
docker export nodejs -o nodejs.tar
tar xf nodejs.tar
rm -rf nodejs.tar
cp ${DIR}/node.sh ${BUILD_DIR}/bin/
sed 's|#!/.*|#!/snap/rocketchat/current/nodejs/bin/node.sh|g' -i ${BUILD_DIR}/usr/local/bin/npm
ls -la ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
