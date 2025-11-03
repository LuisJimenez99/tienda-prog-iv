# .gunicorn_config.py
workers = 4  # Número de procesos (ajustable)
threads = 2  # Hilos por proceso
worker_class = 'sync'
timeout = 120
keepalive = 5
loglevel = 'info'