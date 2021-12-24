#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|post-start]"
    exit 1
fi

. $SNAP_COMMON/config/rocketchat.env

function wait_for_mongo() {
    echo "waiting for mongo db"
    set +e
    for i in $(seq 1 30); do
      ${DIR}/mongodb/bin/mongo.sh localhost/rocketchat ${SNAP_COMMON}/config/mongo.configure.js
      if [[ $? == 0 ]]; then
        started=1
        break
      fi
      echo "Tried $i times. Waiting 5 secs..."
      sleep 5
    done
    set -e
    if [[ $started == 0 ]]; then
        exit 1
    fi
}

case $1 in
start)
    started=0
    wait_for_mongo
    echo "MONGO_URL: $MONGO_URL" | logger -t rocketchat
    echo "MONGO_OPLOG_URL: $MONGO_OPLOG_URL" | logger -t rocketchat
    #exec ${DIR}/nodejs/bin/node ${DIR}/bundle/main.js 2>&1
    started=0
    set +e
    for i in $(seq 1 30); do
      ${DIR}/nodejs/bin/node.sh ${DIR}/bundle/main.js;
      if [[ $? == 0 ]]; then
        started=1
        break
      fi
      echo "Tried \$i times. Waiting 5 secs...";
      sleep 5;
    done
    set -e
    if [[ $started == 0 ]]; then
        exit 1
    fi
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac
