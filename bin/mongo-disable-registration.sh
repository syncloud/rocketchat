#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

. /var/snap/rocketchat/current/config/rocketchat.env
${DIR}/mongodb/bin/mongo.sh localhost/rocketchat /snap/rocketchat/current/config/mongo.disable-registration.js
