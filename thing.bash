#!/bin/bash

# rsync -a --dry-run dist/ $SERVER_USER@$SERVER_IP:/var/www/frontend/Tasklists/dist
ssh -i ${KEY_PATH} -oStrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} '
cd /var/www/
git pull
'