#!/bin/sh -e
DIR=$( cd "$( dirname "$0" )" && cd .. && pwd )
exec ${DIR}/lib/ld-musl-*.so.1 \
  --library-path ${DIR}/lib:${DIR}/usr/lib:${DIR}/usr/local/lib \
  ${DIR}/usr/local/bin/node "$@"
