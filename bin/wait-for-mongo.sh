#!/bin/bash

. /var/snap/rocketchat/current/config/rocketchat.env

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
