#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

ulimit -n 64000
exec ${DIR}/mongodb/bin/mongod.sh --config /snap/rocketchat/current/config/mongodb.conf/rocketchat.env

