#!/bin/bash -e
DIR=$( cd "$( dirname "$0" )" && pwd )

${DIR}/../apt.sh sshpass openssh-client
${DIR}/../retry.sh pip install -r ${DIR}/requirements.txt
