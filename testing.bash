#!/usr/bin/env bash
python3 -m pytest end-to-end-server-stuffs/server-stuffs/server_stuffs/tests/session_tests.py
python3 -m pytest end-to-end-server-stuffs/server-stuffs/server_stuffs/tests/task_tests.py
python3 -m pytest end-to-end-server-stuffs/server-stuffs/server_stuffs/tests/tasklist_tests.py
python3 -m pytest end-to-end-server-stuffs/server-stuffs/server_stuffs/tests/user_tests.py