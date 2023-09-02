"""
coding:utf-8
file: utils.py
@time: 2023/9/2 16:19
@desc:
"""
from flask import jsonify


class ResultJson:
    def ok(self, data=None, **kwargs):
        return jsonify(dict(code=200, msg='OK', data=data, **kwargs))

    def not_found(self, msg='Record not found.', **kwargs):
        return jsonify(dict(code=404, msg=msg, **kwargs))

    def bad_request(self, msg='Bad request.', **kwargs):
        return jsonify(dict(code=400, msg=msg, **kwargs))

    def unauthorized(self, msg='Unauthorized.', **kwargs):
        return jsonify(dict(code=401, msg=msg, **kwargs))

    def forbidden(self, msg='Forbidden.', **kwargs):
        return jsonify(dict(code=403, msg=msg, **kwargs))

    def server_error(self, msg='Server error.', **kwargs):
        return jsonify(dict(code=500, msg=msg, **kwargs))
