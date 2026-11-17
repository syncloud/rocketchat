#!/bin/bash -e

APP_DOMAIN=$1

for i in $(seq 1 120); do
  CODE=$(curl -sk -o /dev/null -w '%{http_code}' "https://${APP_DOMAIN}" || true)
  if [ "$CODE" = "200" ]; then
    echo "${APP_DOMAIN} is ready"
    exit 0
  fi
  echo "waiting for ${APP_DOMAIN}, got ${CODE}"
  sleep 5
done

echo "${APP_DOMAIN} did not become ready"
exit 1
