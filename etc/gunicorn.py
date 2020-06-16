bind = "0.0.0.0:8000"
workers = 4
timeout = 30
error_logfile = "-"
access_logfile = "/opt/logs/ecm-access.log"
chdir = "/opt/ecm"
pythonpath = "/opt/ecm/:/opt/venv/lib/:/opt/venv/lib/python3.8"
