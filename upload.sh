#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

app=$1
branch=$2
build_number=$3
FILE_NAME=$4
bucket=apps.syncloud.org

if [ "${branch}" == "master" ] || [ "${branch}" == "stable" ] ; then

  s3cmd put $FILE_NAME s3://${bucket}/apps/$FILE_NAME
  
  if [ "${branch}" == "stable" ]; then
    branch=rc
  fi

  printf ${build_number} > ${app}.version
  s3cmd put ${app}.version s3://${bucket}/releases/${branch}/${app}.version

fi
