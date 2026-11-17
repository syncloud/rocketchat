#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

VERSION=$1

BUILD_DIR=${DIR}/../build/snap/rocketchat

rm -rf ${BUILD_DIR}
mkdir -p ${BUILD_DIR}/bin

cp -r /app ${BUILD_DIR}/app
cp -r /usr ${BUILD_DIR}/usr
cp -r /lib ${BUILD_DIR}/lib
if [ -d /lib64 ]; then cp -r /lib64 ${BUILD_DIR}/lib64; fi

rm -rf ${BUILD_DIR}/usr/src

IMG=${BUILD_DIR}/app/bundle/programs/server/npm/node_modules/@img
for d in ${IMG}/sharp-linuxmusl-* ${IMG}/sharp-libvips-linuxmusl-*; do
  [ -d "$d" ] || continue
  alias=$(echo "$d" | sed 's/linuxmusl/linux/')
  [ -e "$alias" ] || cp -r "$d" "$alias"
done

for musl in ${BUILD_DIR}/app/bundle/programs/server/npm/node_modules/isolated-vm/prebuilds/linux-*/isolated-vm.*.musl.node; do
  cp -f "$musl" "$(echo "$musl" | sed 's/\.musl\.node$/.glibc.node/')"
done

LICENSE_MODULES=${BUILD_DIR}/app/bundle/programs/server/npm/node_modules/@rocket.chat/license/dist/modules.js
sed -i "s/function hasModule(module) {/function hasModule(module) { if (module === 'oauth-enterprise') { return true; }/" ${LICENSE_MODULES}
grep -q "if (module === 'oauth-enterprise') { return true; }" ${LICENSE_MODULES}

LICENSE_SETTINGS=${BUILD_DIR}/app/bundle/programs/server/app/app.js
sed -i "s/function changeSettingValue(record) {/function changeSettingValue(record) { if (record.modules?.includes('oauth-enterprise')) { return record.value; }/" ${LICENSE_SETTINGS}
grep -q "record.modules?.includes('oauth-enterprise')" ${LICENSE_SETTINGS}

sed -i "s/mapSSOGroupsToChannels(user, identity, groupClaimName, channelsMap, channelsAdmin) {/mapSSOGroupsToChannels(user, identity, groupClaimName, channelsMap, channelsAdmin) { return;/" ${LICENSE_SETTINGS}
grep -q "mapSSOGroupsToChannels(user, identity, groupClaimName, channelsMap, channelsAdmin) { return;" ${LICENSE_SETTINGS}

cp ${DIR}/bin/* ${BUILD_DIR}/bin

echo $VERSION > ${BUILD_DIR}/rocketchat.version
