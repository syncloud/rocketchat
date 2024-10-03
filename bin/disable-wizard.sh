#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

${DIR}/mongodb/bin/mongo.sh localhost/rocketchat $DIR/config/mongo.disable-wizard.js
