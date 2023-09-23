"""
coding:utf-8
file: tools.py
@time: 2023/9/20 23:45
@desc:
"""
from flask import Blueprint, request, send_from_directory
from wms.utils import ResultJson, config, get_uuid
import os
from wms.decorators import path_existed
from urllib.parse import urljoin

tools_bp = Blueprint('tools_bp', __name__, url_prefix='/tools')


@tools_bp.route('/upload-img', methods=['POST'])
@path_existed(config.get('img.save'))
def upload_img():
    file = request.files.get('file')
    uuid = request.form.get('uuid')
    if not file or not uuid:
        return ResultJson.bad_request(msg='参数错误！')
    save_root = os.path.join(config.get('img.save'), uuid)
    if not os.path.exists(save_root):
        os.makedirs(save_root)
    path = os.path.join(save_root, get_uuid() + os.path.splitext(file.filename)[-1])
    file.save(path)
    url = urljoin(config.get('system.host'), 'tools/load-img/' + os.path.join(uuid, os.path.basename(path)))
    return ResultJson.ok(msg='图片上传成功！', url=url)


@tools_bp.route('/load-img/<path:path>')
def load_img(path):
    return send_from_directory(config.get('img.save'), path)
