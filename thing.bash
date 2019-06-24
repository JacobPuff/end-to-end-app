#!/bin/bash

ssh -i ${KEY_PATH} -oStrictHostKeyChecking=no ubuntu@3.18.103.85 '
cd /var/www/
git pull
cd /var/www/end-to-end-server-stuffs/env/bin/
source activate
echo "Activate virtualenv"
cd /var/www/end-to-end-server-stuffs/server-stuffs
gunicorn --bind=localhost:8000 --workers=2 test-gunicorn:guninstuffs
echo "Activate gunicorn stuffs"
'