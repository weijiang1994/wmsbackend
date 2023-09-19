"""
coding:utf-8
file: material.py
@time: 2023/9/17 23:36
@desc:
"""
from flask import Blueprint, request
from wms.decorators import get_params
from wms.utils import ResultJson
material_bp = Blueprint('material_bp', __name__, url_prefix='/material')


@material_bp.route('/upload-img', methods=['POST'])
def upload_img():
    file = request.files
    return ResultJson.ok(msg='图片上传成功！', url='')
