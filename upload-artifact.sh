#!/bin/bash -e

if [ -z "$ARTIFACT_SSH_KEY" ]; then
  echo "ARTIFACT_SSH_KEY must be set"
  exit 1
fi

if [ -z "$3" ]; then
  echo "usage $0 app src dst"
  exit 1
fi

APP=$1
SRC=$2
DST=$3

if [ ! -d $SRC ]; then
    echo "nothing to upload, $SRC does not exist"
    exit 0
fi

echo "$ARTIFACT_SSH_KEY" | base64 --decode > artifact_ssh.key
chmod 600 artifact_ssh.key
chmod -R a+r $SRC
scp -r -oStrictHostKeyChecking=no -i artifact_ssh.key $SRC artifact@artifact.syncloud.org:/home/artifact/repo/$APP/ci/$DST
