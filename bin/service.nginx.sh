#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|stop]"
    exit 1
fi

. /var/snap/rocketchat/current/config/rocketchat.env

function wait_for_server() {
    echo "waiting for server"
    started=0
    set +e
    for i in $(seq 1 60); do
      echo > /dev/tcp/localhost/$PORT
      if [[ $? == 0 ]]; then
        echo "started"
        started=1
        break
      fi
      echo "Tried $i times. Waiting 5 secs..."
      sleep 5
    done
    set -e
    if [[ $started == 0 ]]; then
        echo "failed to start"
        exit 1
    fi
}

case $1 in
start)
    wait_for_server
	  /bin/rm -f /var/snap/rocketchat/common/web.socket
    exec ${DIR}/nginx/sbin/nginx -c /snap/rocketchat/current/config/nginx.conf -p ${DIR}/nginx -g 'error_log stderr warn;'
    ;;
reload)
    ${DIR}/nginx/sbin/nginx -c /snap/rocketchat/current/config/nginx.conf -s reload -p ${DIR}/nginx
    ;;
stop)
    ${DIR}/nginx/sbin/nginx -c /snap/rocketchat/current/config/nginx.conf -s stop -p ${DIR}/nginx
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac
