#!/usr/bin/env python3
# updates time limits in cmsdb

import getopt
import os
import re
import sys
import json

import psycopg2
from psycopg2.extras import Json


DB_HOST='localhost'
PROBLEMS_DIR='../../problems'

def usage():
    print('usage:{} problem_name'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error: {}'.format(s), file=sys.stderr)
    sys.exit(-1)

def update_problems(fname):
    for root, dirs, files in os.walk(fname):
        for dir in dirs:
            m = re.match('[0-9]+f.p[j12s]',dir)
            if m:
                #print('update',os.path.join(root,dir))
                update_problem(os.path.join(root,dir))

def update_problem(fname):
    '''Updates timelimits for a problem '''
    print(f'update timelimit for problem {fname}...',end="", file=sys.stderr)
    pname = os.path.split(fname)[-1]

    cmsinfo = {}
    cmsfile = os.path.join(PROBLEMS_DIR, fname, "attic", "cms.txt")
    if os.path.isfile(cmsfile):
        with open(cmsfile) as f:
            code = compile(f.read(), cmsfile, 'exec')
            exec(code,cmsinfo)

    if 'time_limit_c' in cmsinfo.keys():
        # cms.txt must define all limits
        time_limits["C17 / gcc"] = cmsinfo['time_limit_c']
        time_limits["C++17 / g++"] = cmsinfo['time_limit_c']
        #time_limits["Pascal / fpc"] = cmsinfo['time_limit_c']
        
        time_limits["Java / JDK"] =  cmsinfo['time_limit_java']
        time_limits["Javascript"] =  cmsinfo['time_limit_javascript']
        time_limits["Python 3 / CPython"] =  cmsinfo['time_limit_python']
    else:
        limitsfile = os.path.join(PROBLEMS_DIR, fname,"attic", "problem.desc")
        #with open(limitsfile, "r") as f:
        #    print(f.read())
        if not os.path.isfile(limitsfile):
            print(f"ERROR: could not find time limit for task {pname} (to fix, run 'box check' on the problem)", file=sys.stderr)
            sys.exit(2)
    
        limits = {}
        with open(limitsfile, "r") as f:
            code = compile(f.read(), limitsfile, 'exec')
            exec(code,limits)        
            
        time_limits = {}
        if not limits['time_limit_c']:
            print('ERROR: no time_limit_c for problem', fname)
            return
        time_limits["C17 / gcc"] = limits['time_limit_c']
        time_limits["C++17 / g++"] = limits['time_limit_c']
        #time_limits["Pascal / fpc"] = limits['time_limit_c']

        time_limits["Java / JDK"] =  limits['time_limit_java']
        time_limits["Javascript"] =  limits['time_limit_javascript']
        time_limits["Python 3 / CPython"] =  limits['time_limit_python']

    name = os.path.split(fname)[-1]

    try:
        connection = psycopg2.connect("dbname='cmsdb' user='cmsuser' host={} password='guga.LC'".format(DB_HOST))
    except:
        print("unable to connect")
    connection.set_client_encoding('UTF8')
    cursor = connection.cursor()

    comm = f"select time_limit_lang from datasets as d, tasks as t where t.id=d.task_id and t.name = '{name}'"
    cursor.execute(comm)
    old_time_limit = cursor.fetchone()[0]
    #print("old_time_limit",old_time_limit)
    
    strjson = str(time_limits).replace("'",'"')
    
    comm = f"update datasets set time_limit_lang = '{strjson}' where id in (select d.id from datasets as d, tasks as t where t.id=d.task_id and t.name = '{name}')"
    cursor.execute(comm)
    
    comm = f"select time_limit_lang from datasets as d, tasks as t where t.id=d.task_id and t.name = '{name}'"
    print(comm,file=sys.stderr)
    cursor.execute(comm)
    time_limit = cursor.fetchone()[0]
    print("time_limit",time_limit,file=sys.stderr)
    connection.commit()
    connection.close()
    print(file=sys.stderr)
    print(time_limits, file=sys.stderr)
    print("OK\n", file=sys.stderr)
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r", ["reset"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    reset = False
    for o, a in opts:
        if o in ("-r", "--reset"):
            reset = True
        else:
            assert False, "unhandled option"

    try:
        fname = args[0]
    except:
        print('error: need a dirname',file=sys.stderr)
        usage()


    if fname[-1] == '/':
        fname = fname[:-1]

    tmp = os.path.split(fname)
    tmp = tmp[-1]
    update_problem(fname)

if __name__ == "__main__":
    main()
