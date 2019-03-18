#!/bin/sh

cd /home/pi/cephalon/python-mechanic
tmux new -s RecoveryBot -d
tmux send-keys -t RecoveryBot 'python3.6 recovery.py' C-m
