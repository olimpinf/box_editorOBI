#!/usr/bin/env python3
# encoding: utf-8

import sys

for line in sys.stdin.readlines():
    if line.lstrip() != line:
        sys.exit(1)
