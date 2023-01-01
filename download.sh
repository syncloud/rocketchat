#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

VERSION=$1

BUILD_DIR=${DIR}/build/snap
mkdir -p $BUILD_DIR

wget https://cdn-download.rocket.chat/build/rocket.chat-$VERSION.tgz -O $DIR/node/rocketchat.tar.gz
