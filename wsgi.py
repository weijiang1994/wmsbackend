"""
coding:utf-8
file: wsgi.py
@time: 2023/10/22 13:54
@desc:
"""
from wms import create_app

app = create_app('production')
