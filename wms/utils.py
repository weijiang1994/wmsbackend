"""
coding:utf-8
file: utils.py
@time: 2023/9/2 16:19
@desc:
"""
import os
from wms.settings import basedir
from flask import jsonify
import yaml
import copy
import uuid


class ResultJson:
    @staticmethod
    def ok(data=None, msg='OK', **kwargs):
        return jsonify(dict(code=200, msg=msg, data=data, **kwargs))

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


class Config:

    def __init__(self):
        self.config = None
        self.load()
        self.HOST = self.get('system.host')

    def load(self):
        config_path = os.path.join(basedir, 'config/config.yaml')
        if not os.path.exists(config_path):
            raise Exception(f'请先配置系统配置文件，在{basedir}路径下创建config/config.yaml文件')
        with open(os.path.join(basedir, 'config/config.yaml'), encoding='utf8') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def get(self, key_list: str):
        key_list = key_list.split('.')
        result = copy.deepcopy(self.config)
        for key in key_list:
            result = result.get(key)
            if not result:
                break
        return result


def get_uuid():
    return str(uuid.uuid4()).replace('-', '')


config = Config()


class Const:
    MATERIAL_STATUS = {0: '充足', 1: '告警', 2: '缺乏', 3: '无余量'}


const = Const()
