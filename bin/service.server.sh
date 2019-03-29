#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|post-start]"
    exit 1
fi

. $SNAP_COMMON/config/rocketchat.env

case $1 in
pre-start)
    timeout 300 /bin/bash -c 'until echo > /dev/tcp/localhost/'$MONGO_PORT'; do sleep 1; done'
    timeout 100 /bin/bash -c 'until [ -S '$MONGO_SOCKET_FILE' ]; do echo "waiting for ${MONGO_SOCKET_FILE}"; sleep 1; done'
    ;;
start)
    echo "MONGO_URL: $MONGO_URL" | logger -t rocketchat
    exec ${DIR}/nodejs/bin/node ${DIR}/bundle/main.js 2>&1
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac