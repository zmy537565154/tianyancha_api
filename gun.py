import gevent.monkey

gevent.monkey.patch_all()

import multiprocessing

# debug = True
loglevel = 'debug'
bind = "0.0.0.0:10002"
accesslog = "/etc/supervisor/logs/Enterprise_genealogy_out.log"
errorlog = "/etc/supervisor/logs/Enterprise_genealogy_out.log"
daemon = False

# 启动的进程数
workers = multiprocessing.cpu_count()
worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'
