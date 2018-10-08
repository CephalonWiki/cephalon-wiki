#!/bin/sh

cd ../python-mechanic
tmux new -s TestBot -d
tmux send-keys -t TestBot 'python3.6 test.py' C-m
