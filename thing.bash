#!/bin/bash

ssh -i ${KEY_PATH} -oStrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} '
cd /var/www/
git pull
'
rsync -a --dry-run -r "ssh -i ${KEY_PATH}" dist/ ${SERVER_USER}@${SERVER_IP}:/var/www/frontend/Tasklists/dist