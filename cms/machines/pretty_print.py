#!/usr/bin/env python3.11

import json
import pprint
import sys

data = sys.stdin.read()
data = json.loads(data)
# print json to screen with human-friendly formatting
pprint.pprint(data, compact=False, sort_dicts=False)
