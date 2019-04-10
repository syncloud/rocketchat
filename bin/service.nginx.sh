#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|stop]"
    exit 1
fi

. $SNAP_COMMON/config/rocketchat.env

case $1 in
pre-start)
    timeout 2000 /bin/bash -c 'until echo > /dev/tcp/localhost/'$PORT'; do sleep 1; done'
    /bin/rm -f ${SNAP_COMMON}/web.socket
    exec ${DIR}/nginx/sbin/nginx -t -c ${SNAP_COMMON}/config/nginx.conf -p ${DIR}/nginx -g 'error_log '${SNAP_COMMON}'/log/nginx_error.log warn;'
    ;;
start)
    exec ${DIR}/nginx/sbin/nginx -c ${SNAP_COMMON}/config/nginx.conf -p ${DIR}/nginx -g 'error_log '${SNAP_COMMON}'/log/nginx_error.log warn;'
    ;;
post-start)
    timeout 5 /bin/bash -c 'until [ -S '${SNAP_COMMON}'/web.socket ]; do echo "waiting for ${SNAP_COMMON}/web.socket"; sleep 1; done'
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
