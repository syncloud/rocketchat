#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

VERSION=$1

BUILD_DIR=${DIR}/build/snap
mkdir -p $BUILD_DIR


