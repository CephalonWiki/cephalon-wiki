#!/bin/sh

cd /home/pi/Documents/Cephalon\ Wiki/python-mechanic
tmux new -s CephalonWiki -d
tmux send-keys -t CephalonWiki 'python3.6 start.py' C-m