#!/usr/bin/env python3
# encoding: utf-8

import sys

for line in sys.stdin.readlines():
    if line.endswith('\n\r') or line.endswith('\r\n'):
        sys.exit(1)
    if not line.endswith('\n'):
        sys.exit(1)
