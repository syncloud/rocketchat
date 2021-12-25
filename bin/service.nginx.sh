#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|stop]"
    exit 1
fi

. $SNAP_COMMON/config/rocketchat.env

function wait_for_server() {
    echo "waiting for server"
    started=0
    set +e
    for i in $(seq 1 30); do
      echo > /dev/tcp/localhost/$PORT
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
    wait_for_server
	  /bin/rm -f ${SNAP_COMMON}/web.socket
    exec ${DIR}/nginx/sbin/nginx -c ${SNAP_COMMON}/config/nginx.conf -p ${DIR}/nginx -g 'error_log '${SNAP_COMMON}'/log/nginx_error.log warn;'
    ;;
reload)
    ${DIR}/nginx/sbin/nginx -c ${SNAP_COMMON}/config/nginx.conf -s reload -p ${DIR}/nginx
    ;;
stop)
    ${DIR}/nginx/sbin/nginx -c ${SNAP_COMMON}/config/nginx.conf -s stop -p ${DIR}/nginx
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac
