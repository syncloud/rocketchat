#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start]"
    exit 1
fi

. $SNAP_COMMON/config/rocketchat.env

case $1 in
start)
    exec ${DIR}/mongodb/bin/mongod --quiet --config ${SNAP_COMMON}/config/mongodb.conf
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac