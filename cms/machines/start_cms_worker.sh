#!/bin/sh

CONTEST=4

# kill old session
tmux kill-session -t ssh_tmux

# create new session
tmux new-session -d -s ssh_tmux -n LogService "cmsResourceService -a ${CONTEST}"




