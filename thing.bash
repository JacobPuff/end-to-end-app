#!/bin/bash
cat ${KEY_PATH}
ssh -i ${KEY_PATH} -oStrictHostKeyChecking=no ubuntu@3.18.103.85 '
echo {1..10}
echo {1..5}
cd /var/www/
git pull
'