#!/bin/bash

retry=0
retries=100
APP=rocketchat
NEXT=/snap/$APP/current/version
CURRENT=/var/snap/$APP/current/version
while ! diff $NEXT $CURRENT; do
    if [[ $retry -gt $retries ]]; then
	    echo "waiting for snap configure failed after $retry attempts (current: $(cat $CURRENT), next $(cat $NEXT))"
        exit 1
    fi
    retry=$((retry + 1))
    echo "waiting for snap configure $retry/$retries (current: $(cat $CURRENT), next $(cat $NEXT))"
    sleep 2
done
echo "snap is configured (current: $(cat $CURRENT), next $(cat $NEXT))"
