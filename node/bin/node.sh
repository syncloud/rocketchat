#!/bin/bash -e
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
LIBS=$(echo ${DIR}/lib/*-linux-gnu*)
LIBS=$LIBS:$(echo ${DIR}/usr/lib/*-linux-gnu*)
LIBS=$LIBS:${DIR}/usr/local/lib
${DIR}/lib/*-linux*/ld-*.so* --library-path $LIBS ${DIR}/usr/local/bin/node "$@"