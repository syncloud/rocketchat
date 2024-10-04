#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

$DIR/bin/wait-for-configure.sh

. /var/snap/rocketchat/current/config/rocketchat.env

if [[ -f /var/snap/platform/current/CI_TEST ]]; then
  export NODE_EXTRA_CA_CERTS=/var/snap/platform/current/syncloud.ca.crt
fi

echo "starting server"
started=0
set +e
for i in $(seq 1 30); do
  ${DIR}/node/bin/node.sh ${DIR}/node/rocketchat/main.js
  if [[ $? == 0 ]]; then
    started=1
    break
  fi
  echo "Tried $i times. Waiting 5 secs...";
  sleep 5;
done
set -e
if [[ $started == 0 ]]; then
    exit 1
fi
