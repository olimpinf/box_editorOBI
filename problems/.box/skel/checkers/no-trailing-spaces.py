#!/usr/bin/env python3
# encoding: utf-8

import sys

for line in sys.stdin.readlines():
    if line.endswith('\n'):
        line = line[:-1]
    if line.rstrip() != line:
        sys.exit(1)
