#!/bin/sh

CONTEST=1

# kill old session
tmux kill-session -t ssh_tmux

# create new session
tmux new-session -d -s ssh_tmux -n LogService "cmsLogService | tee LOG  2>&1"
tmux new-window -d -n ResourceService -t ssh_tmux: "cmsResourceService -a ${CONTEST}"


