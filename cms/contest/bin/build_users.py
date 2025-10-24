#!/usr/bin/env python3

import csv
import sys
import re
import os
import getopt
import shutil
from datetime import datetime
from glob import glob
from functools import cmp_to_key


def usage():
    print('usage:\n  {} [-h] [-u users] contest_description_file'.format(sys.argv[0]))
    sys.exit(2)


def read_users(filename):
    if not os.path.isfile(filename):
        print(f"ERROR: file {filename} not found", file=sys.stderr)
        sys.exit(2)
    try:
        csvf = open(filename,"r", encoding='utf-8')
        #print('utf-8')
    except:
        try:
            csvf = open(filename,"r", encoding='iso8859-1')
            #print('iso8859-1')
        except:
            msg = f'ERROR: Problema na decodificação do arquivo "{filename}". Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
            print(msg, file=sys.stderr)
            sys.exit(2)
    
    reader = csv.reader(csvf) #, delimiter=delimiter)
    linenum=0
    users = []
    for r in reader:
        linenum += 1
        if len(r)==0:
            continue
        try:
            username = r[0].strip()
            password = r[1].strip()
            name = r[2].strip()
        except:
            print(f"ERROR: problem in user file {filename}, line {linenum}: {r}")
            sys.exit(2)
        if id == 'user_id':
            # first line
            continue

        tks = name.split()
        first = tks[0]
        last = " ".join(tks[1:])
        users.append((username,password,'null',first,last))

    return users

def compare_grp(a,b):
    a = int(os.path.basename(a))
    b = int(os.path.basename(b))
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0

def compare_tst(a,b):
    a = int(os.path.basename(a).split('.')[0])
    b = int(os.path.basename(b).split('.')[0])
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:", ["help","users"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
    contest_description = "Contest Description"
    users_file = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-u", "--users"):
            users_file = a
        else:
            assert False, "unhandled option"

    if len(args) == 1:
        contest_descr_file = args[0]
    else:
        usage()

    if not os.path.exists(contest_descr_file):
        usage()

    contest_descr = {}
    with open(contest_descr_file) as f:
        code = compile(f.read(), contest_descr_file, 'exec')
        exec(code,contest_descr)

    contest_name = contest_descr['name']
    contest_description = contest_descr['description']
    if os.path.exists(contest_name):
        print(f'directory {contest_name} exists and will be cleaned. Proceed? [Y/n]', file=sys.stderr, end=' ')
        answer = input().strip()
        if (not answer) or answer in ('Y','y'):
            shutil.rmtree(contest_name)
        else:
            print('directory not cleaned, exiting', file=sys.stderr)
            sys.exit(0)
    os.mkdir(contest_name)
    base = os.curdir

    ##############
    # contest.yaml
    ##############
    fcontest = open(os.path.join(base, contest_name, "contest.yaml"), "w")

    for k in contest_descr.keys():
        if k == '__builtins__':
            continue
        elif k == 'start':
            date = datetime.fromisoformat(contest_descr[k])
            timestamp = int(date.timestamp())
            print(f'{k}: {timestamp}', file=fcontest)
            continue
        elif k == 'stop':
            date = datetime.fromisoformat(contest_descr[k])
            timestamp = int(date.timestamp())
            print(f'{k}: {timestamp}', file=fcontest)
            continue
        try:
            print(f'{k}: {int(contest_descr[k])}', file=fcontest)
        except:
            print(f'{k}: "{contest_descr[k]}"', file=fcontest)
    
    print(f'tasks:', file=fcontest)
    # problems
    
    problems = contest_descr['problems']
    for pname in problems:
        #pname = os.path.basename(problem)
        print(f'  - "{pname}"', file=fcontest)

    # users
    print(f'users:', file=fcontest)
    if users_file == "":
        users = [("u1","p1","null"),("u2","p2","null")]
    else:
        users = read_users(users_file)
    for u in users:
        print(f'  - username: "{u[0]}"', file=fcontest)
        print(f'    password: "{u[1]}"', file=fcontest)
        #print(f'    password_method: "plain"', file=fcontest)
        print(f'    ip: {u[2]}', file=fcontest)
        if len(u) >= 4:
            print(f'    first_name: "{u[3]}"', file=fcontest)
        if len(u) >= 5:
            print(f'    last_name: "{u[4]}"', file=fcontest)


if __name__ == "__main__":
    main()
