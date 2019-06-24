#!/bin/bash

ssh -i ${KEY_PATH} -oStrictHostKeyChecking=no ubuntu@3.18.103.85 '
cd /var/www/
git pull
'