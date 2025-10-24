#!/usr/bin/env python

import getopt
import os
import re
import subprocess
import sys
import importlib


#CMS_PATH = "/home/cms/cms_venv/box_obi2025/prog/fase-2/cms/machines"
CMS_PATH = os.getcwd()

def usage():
    print(f'usage:{sys.argv[0]} level config_file', file=sys.stderr)
    sys.exit(-1)

def error(s):
    print(f'error: {s}', file=sys.stderr)
    sys.exit(-1)


def sync_config(machines, fconfig):
    '''Sync cms config '''

    print(f"using {CMS_PATH}")
    print(f"Copying {fconfig}")

    mainserver = machines.mainserver
    evaluationserver = machines.evaluationserver
    webservers = machines.webservers
    workers = machines.workers    
    
    allservers = set()
    allservers.add(mainserver)
    allservers.add(evaluationserver)
    for (s,n) in webservers:
        allservers.add(s)
    for (s,n) in workers:
        allservers.add(s)

    for m in allservers:
        cmd = f"scp -q {fconfig} cms@{m}:/usr/local/etc/cms.conf"

        try:
            output = subprocess.check_output(cmd, shell=True)
        except Exception as e:
            print(f"ERROR when copying to machine {m} ({e})")
            continue

        if m == mainserver:
            machinename = 'mainserver'
        elif m == evaluationserver:
            machinename = 'evaluationserver'
        else:
            machinename = 'worker'
        print(f"{machinename} ({m}) ok")


def start_cms(machines):

    print(f"\nStart cms")
    print(f"Using {CMS_PATH}\n")

    mainserver = machines.mainserver
    evaluationserver = machines.evaluationserver
    webservers = machines.webservers
    workers = machines.workers
    
    workers_set = set()
    for (s,n) in workers:
        workers_set.add(s)

    # start cms in workers
    print("\n-------")
    print("workers")
    print("-------")
    for m in workers_set:
        machinename = 'worker'

        cmd = f'scp /home/cms/bin/start_cms_worker.sh cms@{m}:/home/cms/bin/start_cms_worker.sh'

        try:
            output = subprocess.check_output(cmd, shell=True)
            output = output.decode("utf-8")
        except Exception as e:
            print(f"ERROR when copying start scritp to  {m} ({e})")
        
        cmd = f'''ssh -q -tt cms@{m} <<'EOF'                                                                                                               
cd cms_venv; source bin/activate;
/home/cms/bin/start_cms_worker.sh;
logout;
EOF'''
        try:
            output = subprocess.check_output(cmd, shell=True)
            output = output.decode("utf-8")
            print(f"{machinename} ({m}) ok")
        except Exception as e:
            print(f"ERROR when starting cms in machine {m} ({e})")

    # now start cms in the main server
    print("\n-------")
    print("main server")
    print("-------")
    machinename = 'mainserver'
    m = mainserver
    cmd = f'''ssh -q -tt cms@{mainserver} <<'EOF'                                                                                                               
cd cms_venv; source bin/activate;
/home/cms/bin/start_cms.sh;
logout;
EOF'''
    try:
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode("utf-8")
        print(f"{machinename} ({m}) ok")


    except Exception as e:
        print(f"ERROR when starting cms in machine {m} ({e})")

    print("\ndone\n")



def terminate_cms(machines):

    mainserver = machines.mainserver
    evaluationserver = machines.evaluationserver
    webservers = machines.webservers
    workers = machines.workers
    
    allservers = set()
    allservers.add(mainserver)
    allservers.add(evaluationserver)
    for (s,n) in webservers:
        allservers.add(s)
    for (s,n) in workers:
        allservers.add(s)

    # list tmux in workers
    print("Terminate CMS in all machines")
    for m in allservers:
        cmd = f'''ssh -q -tt cms@{m} <<'EOF'                                                                                                               
tmux kill-server;
logout;
EOF'''
        try:
            output = subprocess.check_output(cmd, shell=True)
            print(f"Terminated cms running in machine {m}")
        except Exception as e:
            print(f"There was no cms running in machine {m}")

    print()  

def list_cms(machines):

    mainserver = machines.mainserver
    evaluationserver = machines.evaluationserver
    webservers = machines.webservers
    workers = machines.workers
    
    allservers = set()
    allservers.add(mainserver)
    allservers.add(evaluationserver)
    for (s,n) in webservers:
        allservers.add(s)
    for (s,n) in workers:
        allservers.add(s)

    # list tmux in workers
    print("\n-------")
    print("workers")
    print("-------")
    for m in allservers:
        if m == mainserver:
            continue
        else:
            cmd = f'''ssh -q -tt cms@{m} <<'EOF'                                                                                                               
tmux list-sessions;
logout;
EOF'''
            try:
                output = subprocess.check_output(cmd, shell=True)
                output = output.decode("utf-8")
                lines = output.split('\n')
                for line in lines:
                    if line.find("ssh_tmux")>=0 and line.find(" ") >= 0:
                        print(f"{m}: {line}")
            except Exception as e:
                print(f"ERROR when starting cms in machine {m} ({e})")

    # now list tmux in the main server
    print("\n-------")
    print("main server")
    print("-------")
    cmd = f'''ssh -q -tt cms@{mainserver} <<'EOF'                                                                                                               
tmux list-sessions;
logout;                                                                                                                                                                                                                   
EOF'''

    try:
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode("utf-8")
        lines = output.split('\n')
        for line in lines:
            if line.find("ssh_tmux")>=0 and line.find("window") >= 0:
                print(f"{mainserver}: {line}")
    except Exception as e:
        print(f"ERROR when starting cms in machine {mainserver} ({e})")


    print("done")  

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "lst", ["list", "start", "terminate"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    start = False
    list = False
    terminate = False
    for o, a in opts:
        if o in ("-l", "--list"):
            list = True
        elif o in ("-s", "--start"):
            start = True
        elif o in ("-t", "--terminate"):
            terminate = True
        else:
            assert False, "unhandled option"

    try:
        level = args[0]
        fconfig = args[1]
    except:
        usage()

    if level not in ("pj","p1","p2","ps"):
        usage()

    fname = f'machines_{level}'
    machines = importlib.import_module(fname)

    if list:
        list_cms(machines)
        return

    if terminate:
        terminate_cms(machines)
        return

    sync_config(machines, fconfig)
    if start:
        terminate_cms(machines)
        start_cms(machines)

if __name__ == "__main__":
    main()

