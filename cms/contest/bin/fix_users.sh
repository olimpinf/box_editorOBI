#! /bin/bash

LEVEL=$1

source /home/cms/cms_venv/bin/activate
/home/cms/cms_venv/box_obi2025/prog/fase-1/cms/contest/bin/add_db_users.py 1 /tmp/users_$LEVEL.csv > /tmp/FIXES 2>&1
/home/cms/cms_venv/box_obi2025/prog/fase-1/cms/contest/bin/update_db_passwords.py 1 /tmp/users_$LEVEL.csv >> /tmp/FIXES 2>&1
