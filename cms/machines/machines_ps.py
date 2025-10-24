############
# machines.py
############

# mainserver will host 
# AdminWebserver, LogService, Checker, ProxyService and database
mainserver = "172.31.8.6"

# evaluationserver will host EvaluationService and ScoringService
evaluationserver = "172.31.8.6"

# webservers will host ContestWebServer
webservers = [
    ("172.31.8.6", 4),
]

# workers will host Workers
workers = [
    ("172.31.11.32", 1),
    ("172.31.6.226", 1),
    ("172.31.5.65", 1),
    ("172.31.9.227", 1),
    ("172.31.35.158", 1),
    ("172.31.45.78", 1),
    ("172.31.44.206", 1),
    ("172.31.34.185", 1),
]
