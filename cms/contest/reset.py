#!/usr/bin/env python3

import os
import sys
import subprocess

def usage():
    print("usage: need level as argument (pj, p1...)")
    sys.exit(-1)

exam=sys.argv[1]


filename = f"{exam}.txt"
dirname,ext=os.path.splitext(filename)

# drop CMS DB
if os.system("cmsDropDB") != 0:
    print("Error removing CMS DB")
    sys.exit(-1)
    
# init CMS DB
if os.system("cmsInitDB") != 0:
    print("Error creating CMS DB")
    sys.exit(-1)

###########
# contest

print(f"bin/build_cms.py -u users_dummy.csv {dirname}.txt")
if os.system(f"bin/build_cms.py -u users_dummy.csv {dirname}.txt") != 0:
    print(f"Error building {dirname}")
    sys.exit(-1)
    
if os.system(f"cmsImportUser -A {dirname}") != 0:
    print(f"Error in cmsImportUser -A {dirname}")
    sys.exit(-1)
    
if os.system(f"cmsImportContest --update-contest --import-tasks {dirname}") != 0:
    print(f"Error in cmsImportContest --update-contest --import-tasks {dirname}")
    sys.exit(-1)


###########
# time limits
#

contest_descr = {}
with open(filename) as f:
    code = compile(f.read(), filename, 'exec')
    exec(code,contest_descr)

for problem in contest_descr['problems']:
    if os.system(f"bin/update_time_limits.py {problem}") != 0:
        print(f"error updating time limits for {problem}")

print("\nMake sure you copy the admin password and change it in the web interface!")
print("\n*********")

if os.system(f"cmsAddAdmin olimpinf") != 0:
    print("error generating password")
    sys.exit(-1)
print("*********")

print("\ndone")
