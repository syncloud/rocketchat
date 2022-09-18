#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

apt update
apt -y install patch libglib2.0-0 python build-essential pkg-config glib2.0-dev libexpat1-dev libtool autoconf g++ build-essential cmake
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh  -s -- -y
source "$HOME/.cargo/env"

cd ${DIR}/bundle/programs/server
CXX=g++-4.8 
CC=gcc-4.8
npm install --unsafe-perm --production

yes | rustup self uninstall
apt -y remove patch libglib2.0-0 python build-essential pkg-config glib2.0-dev libexpat1-dev libtool autoconf g++ build-essential cmake
apt -y autoclean
apt -y autoremove
rm -rf npm/node_modules/@rocket.chat/forked-matrix-sdk-crypto-nodejs/target
