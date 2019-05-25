#!/bin/sh

cd /home/pi/cephalon/python-mechanic
tmux new -s CephalonWikiInbox -d
tmux send-keys -t CephalonWikiInbox 'python3.6 inbox.py' C-m
