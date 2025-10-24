############
# machines.py
############

# mainserver will host 
# AdminWebserver, LogService, Checker, ProxyService and database
mainserver = "172.31.4.97"

# evaluationserver will host EvaluationService and ScoringService
evaluationserver = "172.31.4.97"

# webservers will host ContestWebServer
webservers = [
    ("172.31.4.97", 6),
]

# workers will host Workers
workers = [
    ("172.31.12.245", 1),
    ("172.31.8.98", 1),
    ("172.31.8.65", 1),
    ("172.31.1.53", 1),
    ("172.31.3.165", 1),
    ("172.31.3.61", 1),
    ("172.31.11.11", 1),
    ("172.31.2.191", 1),
    ("172.31.34.171", 1),
    ("172.31.33.213", 1),
    ("172.31.41.58", 1),
    ("172.31.45.235", 1),
    ("172.31.44.144", 1),
    ("172.31.46.97", 1),
]
