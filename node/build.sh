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

# rocket.chat ships a musl (Alpine) build; detect-libc misreads the glibc
# syncloud host and makes sharp look for the linux-x64 (glibc) variant, so
# alias the bundled musl sharp packages to the glibc names (the musl .node
# runs fine under the bundled musl node).
IMG=${BUILD_DIR}/app/bundle/programs/server/npm/node_modules/@img
for d in ${IMG}/sharp-linuxmusl-* ${IMG}/sharp-libvips-linuxmusl-*; do
  [ -d "$d" ] || continue
  alias=$(echo "$d" | sed 's/linuxmusl/linux/')
  [ -e "$alias" ] || cp -r "$d" "$alias"
done

cp ${DIR}/bin/* ${BUILD_DIR}/bin

echo $VERSION > ${BUILD_DIR}/rocketchat.version
