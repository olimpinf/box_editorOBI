############
# machines.py
############

# mainserver will host 
# AdminWebserver, LogService, Checker, ProxyService and database
mainserver = "172.31.0.115"

# evaluationserver will host EvaluationService and ScoringService
evaluationserver = "172.31.0.115"

# webservers will host ContestWebServer
webservers = [
    ("172.31.0.115", 6),
]

# workers will host Workers
workers = [
    ("172.31.9.247", 1),
    ("172.31.9.183", 1),
    ("172.31.0.85", 1),
    ("172.31.3.254", 1),
    ("172.31.8.151", 1),
    ("172.31.34.125", 1),
]
