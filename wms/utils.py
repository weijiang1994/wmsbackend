"""
coding:utf-8
file: utils.py
@time: 2023/9/2 16:19
@desc:
"""
from flask import jsonify


class ResultJson:
    @staticmethod
    def ok(data=None, **kwargs):
        return jsonify(dict(code=200, msg='OK', data=data, **kwargs))

    @staticmethod
    def not_found(msg='Record not found.', **kwargs):
        return jsonify(dict(code=404, msg=msg, **kwargs))

    @staticmethod
    def bad_request(msg='Bad request.', **kwargs):
        return jsonify(dict(code=400, msg=msg, **kwargs))

    @staticmethod
    def unauthorized(msg='Unauthorized.', **kwargs):
        return jsonify(dict(code=401, msg=msg, **kwargs))

    @staticmethod
    def forbidden(msg='Forbidden.', **kwargs):
        return jsonify(dict(code=403, msg=msg, **kwargs))

    @staticmethod
    def server_error(msg='Server error.', **kwargs):
        return jsonify(dict(code=500, msg=msg, **kwargs))
