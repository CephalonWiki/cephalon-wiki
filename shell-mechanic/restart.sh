#!/bin/sh

cd /home/pi/cephalon/python-mechanic
tmux kill-session -t CephalonWiki
tmux new -s CephalonWiki -d
tmux send-keys -t CephalonWiki 'python3.6 start.py' C-m
