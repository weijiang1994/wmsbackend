"""
coding:utf-8
file: gunicorn_config.py
@time: 2023/10/22 13:54
@desc:
"""
workers = 4
# 工作模式
worker_class = 'eventlet'
# 打印全部配置
print_config = False
# 日志配置
loglevel = 'info'
accesslog = '/var/log/dashboard/gunicorn_access.log'
errorlog = '/var/log/dashboard/gunicorn_error.log'
pidfile = '/var/log/dashboard/gunicorn.pid'
# 最大并发量
worker_connections = 2000
