#!/bin/bash -e
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
${DIR}/node.sh $DIR/usr/local/bin/npm "$@"
