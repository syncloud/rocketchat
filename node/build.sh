#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

VERSION=$1

BUILD_DIR=${DIR}/../build/snap/node

apt update
apt -y install wget patch libglib2.0-0 python build-essential pkg-config glib2.0-dev libexpat1-dev libtool autoconf g++ build-essential cmake graphicsmagick

wget https://cdn-download.rocket.chat/build/rocket.chat-$VERSION.tgz -O rocketchat.tar.gz
tar xf rocketchat.tar.gz

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh  -s -- -y
source "$HOME/.cargo/env"
rustup install 1.66.0

cd ${DIR}/bundle/programs/server
CXX=g++-4.8
CC=gcc-4.8
npm install --unsafe-perm --production

yes | rustup self uninstall
apt -y remove patch libglib2.0-0 python build-essential pkg-config glib2.0-dev libexpat1-dev libtool autoconf g++ build-essential cmake
apt -y autoclean
apt -y autoremove
rm -rf npm/node_modules/@rocket.chat/forked-matrix-sdk-crypto-nodejs/target

mkdir -p ${BUILD_DIR}
mv ${DIR}/bundle $BUILD_DIR/rocketchat
echo $VERSION > $BUILD_DIR/rocketchat.version

cp /usr ${BUILD_DIR}
cp /lib ${BUILD_DIR}
cp -r ${DIR}/bin ${BUILD_DIR}/bin

ls -la ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
