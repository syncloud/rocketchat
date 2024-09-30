#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|post-start]"
    exit 1
fi

. /var/snap/rocketchat/current/config/rocketchat.env

function wait_for_mongo() {
    echo "waiting for mongo db"
    set +e
    for i in $(seq 1 30); do
      ${DIR}/mongodb/bin/mongo.sh localhost/rocketchat /snap/rocketchat/current/config/mongo.configure.js
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
    echo "done waiting for mongo db"
}

if [[ -f /var/snap/platform/current/CI_TEST ]]; then
  export NODE_EXTRA_CA_CERTS=/var/snap/platform/current/syncloud.ca.crt
fi

case $1 in
start)
    started=0
    wait_for_mongo
    echo "MONGO_URL: $MONGO_URL"
    echo "MONGO_OPLOG_URL: $MONGO_OPLOG_URL"
#    export EXIT_UNHANDLEDPROMISEREJECTION=1
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
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac
