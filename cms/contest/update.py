#!/usr/bin/env python3

import os
import sys
import subprocess

def usage():
    print("usage: need level as argument (pj, p1...)")
    sys.exit(-1)

level=sys.argv[1]

if level not in ('pj','p1','p2','ps'):
    usage()

filename = f"prova_{level}.txt"
dirname,ext=os.path.splitext(filename)

###########
# contest
if os.system(f"./bin/build_cms.py -u users.csv {filename}") != 0:
    print("error building contest")
    sys.exit(-1)

if os.system(f"cmsImportContest --update-contest --import-tasks {dirname}") != 0:
    print("task already present, not imported, will update")

if os.system(f"cmsImportContest --update-contest --update-tasks {dirname}") != 0:
    print("Error while updating, continuing")

###########
# time limits

if level == 'pj':
    problems = ["jogo","teste","carros","digitos"]
elif level == 'p1':
    problems = ["pizza","carros","digitos","pilha"]
elif level == 'p2':
    problems = ["caravana","digitos","pilhas","radares","rodovias"]
elif level == 'ps':
    problems = ["caravana","digitos","quadrado","radares","rodovias_facil"]
else:
    print(f"wrong level {level}")
    sys.exit(-1)

for problem in problems:
    if os.system(f"./bin/update_time_limits.py {problem}") != 0:
        print(f"error updating time limits for problem {problem}")
        sys.exit(-1)

print("\ndone")

