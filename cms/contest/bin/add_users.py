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
from subprocess import call

def usage():
    print('usage:\n  {} [-h] users_file'.format(sys.argv[0]))
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
        if id == 'compet_id':
            # first line
            continue

        tks = name.split()
        first = tks[0]
        last = " ".join(tks[1:])
        users.append((username,password,first,last))

    return users


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:", ["help","users"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        else:
            assert False, "unhandled option"

    if len(args) == 1:
        users_file = args[0]
    else:
        usage()

    if not os.path.exists(users_file):
        usage()

    # users
    users = read_users(users_file)
    for u in users:
        try:
            cmd = f'cmsAddUser -p {u[1]} \"{u[2]}\" \"{u[3]}\" {u[0]}'
            retcode = call(cmd, shell=True)
            if retcode < 0:
                print(f"add {u[0]} was terminated by signal", -retcode, file=sys.stderr)
        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)
        try:
            cmd = f'cmsAddParticipation -c 1 {u[0]}'
            print(cmd)
            retcode = call(cmd, shell=True)
            if retcode < 0:
                print(f"add {u[0]} was terminated by signal", -retcode, file=sys.stderr)
        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)

if __name__ == "__main__":
    main()
