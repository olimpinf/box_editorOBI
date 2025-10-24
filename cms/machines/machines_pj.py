############
# machines.py
############

# mainserver will host 
# AdminWebserver, LogService, Checker, ProxyService and database
mainserver = "172.31.5.67"

# evaluationserver will host EvaluationService and ScoringService
evaluationserver = "172.31.5.67"

# webservers will host ContestWebServer
webservers = [
    ("172.31.5.67", 1),
]

# workers will host Workers
workers = [
    ("172.31.5.67", 1),
    # ("172.31.4.50", 1),
    # ("172.31.6.210", 1),
    # ("172.31.0.108", 1),
    # ("172.31.15.105", 1),
    # ("172.31.39.244", 1),
]
