#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start]"
    exit 1
fi

. /var/snap/rocketchat/current/config/rocketchat.env

case $1 in
start)
    ulimit -n 64000
    exec ${DIR}/mongodb/bin/mongod.sh --config /var/snap/rocketchat/current/config/mongodb.conf
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac

