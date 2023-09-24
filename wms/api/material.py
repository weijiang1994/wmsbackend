"""
coding:utf-8
file: material.py
@time: 2023/9/17 23:36
@desc:
"""
import os

from flask import Blueprint, request, url_for, escape
from wms.decorators import get_params, path_existed
from wms.utils import ResultJson, config, get_uuid
from wms.models import MaterialSpec, User
from urllib.parse import urljoin, unquote
from flask_jwt_extended import current_user, jwt_required

material_bp = Blueprint('material_bp', __name__, url_prefix='/material')


@material_bp.route('/add/spec', methods=['POST'])
@path_existed(config.get('img.save'))
@jwt_required()
def add_spec():
    name = request.json.get('name')
    description = request.json.get('specification')
    uuid = request.json.get('uuid')
    images_path = os.path.join(config.get('img.save'), uuid)
    images = []
    if os.path.exists(images_path):
        images = os.listdir(images_path)
        images = [unquote(url_for('tools_bp.load_img', path=os.path.join(uuid, image))) for image in images]
    if MaterialSpec.query.filter_by(name=name).first():
        return ResultJson.bad_request(msg='规格名称已存在！')
    spec = MaterialSpec(
        name=name,
        description=description,
        images=images,
        user=current_user.id
    )
    spec.save()
    return ResultJson.ok(msg='规格添加成功！')


@material_bp.route('/list/spec')
@get_params(
    params=['page', 'size', 'name'],
    types=[int, int, str]
)
def list_spec(page, size, name):
    if name:
        specs = MaterialSpec.query.join(
            User,
            User.id == MaterialSpec.user
        ).filter(
            MaterialSpec.name.like(f"{name}%")
        ).with_entities(
            MaterialSpec.name,
            MaterialSpec.description,
            MaterialSpec.create_time,
            MaterialSpec.update_time,
            MaterialSpec.images,
            User.name.label('user')
        ).paginate(page=page, per_page=size)
    else:
        specs = MaterialSpec.query.join(
            User,
            User.id == MaterialSpec.user
        ).with_entities(
            MaterialSpec.name,
            MaterialSpec.description,
            MaterialSpec.create_time,
            MaterialSpec.update_time,
            MaterialSpec.images,
            User.name.label('user')
        ).paginate(page=page, per_page=size)
    return ResultJson.ok(
        data=[dict(
            name=spec.name,
            description=spec.description,
            images=[urljoin(config.HOST, img) for img in spec.images],
            create_time=str(spec.create_time),
            update_time=str(spec.update_time),
            user=spec.user
        ) for spec in specs.items],
        total=specs.total
    )
