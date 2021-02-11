#!/bin/bash

ssh -i ${KEY_PATH} -oStrictHostKeyChecking=no ${SERVER_USER}@${SERVER_ADDRESS} '
cd /var/www/
git pull
'