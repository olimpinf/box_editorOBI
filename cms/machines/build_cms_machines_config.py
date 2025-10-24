#!/usr/bin/env python3
# updates time limits in cmsdb

import getopt
import os
import re
import sys
import json
import pprint
import importlib

def usage():
    print(f'usage:{sys.argv[0]} machines.txt', file=sys.stderr)
    sys.exit(-1)

def error(s):
    print(f'error: {s}', file=sys.stderr)
    sys.exit(-1)

def build_config(cmsfile, machines):
    '''Build cms config '''

    mainserver = machines.mainserver
    evaluationserver = machines.evaluationserver
    webservers = machines.webservers
    workers = machines.workers

    ##############
    # core services
    core_services = {}
    port = 29000
    core_services["LogService"] = [[mainserver, port]]


    port = 28000
    core_services["ResourceService"] = []

    allservers = set()
    allservers.add(mainserver)
    allservers.add(evaluationserver)
    for (s,n) in webservers:
        allservers.add(s)
    for (s,n) in workers:
        allservers.add(s)

    for s in sorted(list(allservers)):
        core_services["ResourceService"].append([s,port])


    port = 22000
    core_services["Checker"] = [[mainserver, port]]
    port = 28500
    core_services["ScoringService"] = [[evaluationserver, port]]
    port = 25000
    core_services["EvaluationService"] = [[evaluationserver, port]]
    
    core_services["Worker"] = []
    for (s,n) in sorted(list(workers)):
        port = 26000
        for i in range(n):
            core_services["Worker"].append([s,port])
            port += 1

    core_services["ContestWebServer"] = []
    for (s,n) in sorted(list(webservers)):
        port = 21000
        for i in range(n):
            core_services["ContestWebServer"].append([s,port])
            port += 1

    port = 21100
    core_services["AdminWebServer"] = [[mainserver, port]]
    port = 28600
    core_services["ProxyService"] = [[mainserver, port]]
    port = 25123
    core_services["PrintingService"] = []
        
    core_services = json.dumps(core_services)
    #core_services = pprint.pformat(core_services, compact=False, sort_dicts=True)
    core_services = core_services.replace("{", "\t{\n")
    core_services = core_services.replace("}", "\n\t}")
    core_services = core_services.replace("]],", "]],\n")
    core_services = core_services.replace("],", "],\n\t\t")

    with open("template.conf", "r") as f:
        template = f.read()

    ##############
    # other services
    other_services = {}
    port = 27501
    other_services["TestFileCacher"] = []


    ##############
    # contest_listen_address

    contest_listen_address = []
    for (s,n) in sorted(list(webservers)):
        for i in range(n):
            contest_listen_address.append("")

    port = 8888
    contest_listen_port = []
    for (s,n) in sorted(list(webservers)):
        for i in range(n):
            contest_listen_port.append(port)
            port -= 1


    config = template.format(core_services=core_services, other_services=other_services, mainserver=mainserver, evaluationserver=evaluationserver,
                          contest_listen_address=str(contest_listen_address), contest_listen_port=str(contest_listen_port))
    config = config.replace("'", '"')
    print("{\n" + f"{config}"+ "\n}")
        
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
        level = args[0]
    except:
        usage()

    if level not in ("pj","p1","p2","ps"):
        usage()


    fname = f'machines_{level}'
    machines = importlib.import_module(fname)

    build_config(fname, machines)

if __name__ == "__main__":
    main()

