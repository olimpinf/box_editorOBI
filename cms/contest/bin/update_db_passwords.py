#!/usr/bin/env python3

import csv
import sys
import re
import os
import getopt
import shutil
from datetime import datetime
from glob import glob
from subprocess import call
import psycopg2

DB_HOST='localhost'

def usage():
    print('usage:\n  {} [-h] contest users_file'.format(sys.argv[0]))
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

    if len(args) == 2:
        contest = int(args[0])
        users_file = args[1]
    else:
        usage()

    if not os.path.exists(users_file):
        usage()

    try:
        conn = psycopg2.connect(f"dbname='cmsdb' user='cmsuser' host={DB_HOST} password='guga.LC'")
    except:
        print("unable to connect")
        sys.exit(2)
        
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()

    # users
    users = read_users(users_file)
    preferred_languages = '{}'
    for u in users:

        try:
            cmd = f"select password from  users where username='{u[0]}'" # (first_name, last_name, username, password, preferred_languages) VALUES ('{u[2]}','{u[3]}','{u[0]}','plaintext:{u[1]}','{preferred_languages}') RETURNING id"
            cursor.execute(cmd)
            password = cursor.fetchone()[0]
            if password != f'plaintext:{u[1]}':
                print("differ: ", f'{u[0]}', f'plaintext:{u[1]}', 'current:',password)
                cmd = f"update users set password='plaintext:{u[1]}' where username='{u[0]}'"
                #print(cmd)
                cursor.execute(cmd)
                conn.commit()
            #else:
            #    print("OK: ", f'{u[0]}', f'plaintext:{u[1]}', 'current:',password)
        except Exception as e:
            print(f'failed: {e}')
            conn.rollback()

    
if __name__ == "__main__":
    main()
