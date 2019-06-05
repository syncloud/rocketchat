#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|post-start]"
    exit 1
fi

. $SNAP_COMMON/config/rocketchat.env

export LD_LIBRARY_PATH=${DIR}/lib

case $1 in
start)
    bash -c "for i in \$(seq 1 30); do ${DIR}/mongodb/bin/mongo localhost/rocketchat ${SNAP_COMMON}/config/mongo.configure.js && s=\$? && break || s=\$?; echo \"Tried \$i times. Waiting 5 secs...\"; sleep 5; done; (exit \$s)"

    echo "MONGO_URL: $MONGO_URL" | logger -t rocketchat
    echo "MONGO_OPLOG_URL: $MONGO_OPLOG_URL" | logger -t rocketchat
    #exec ${DIR}/nodejs/bin/node ${DIR}/bundle/main.js 2>&1
    bash -c "for i in \$(seq 1 30); do ${DIR}/nodejs/bin/node ${DIR}/bundle/main.js && s=\$? && break || s=\$?; echo \"Tried \$i times. Waiting 5 secs...\"; sleep 5; done; (exit \$s)"
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac
