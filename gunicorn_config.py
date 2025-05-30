import multiprocessing

# Gunicorn config variables
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = multiprocessing.cpu_count() * 2
max_requests = 1000
timeout = 30