"""
coding:utf-8
file: material.py
@time: 2023/9/17 23:36
@desc:
"""
import os

from flask import Blueprint, request, url_for, escape
from wms.decorators import get_params, path_existed
from wms.utils import ResultJson, config, get_uuid, const
from wms.models import MaterialSpec, User, Material, MaterialIn, Warehouse
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
    query = MaterialSpec.id
    if name:
        query = MaterialSpec.name.like(f"{name}%")
    specs = MaterialSpec.query.join(
        User,
        User.id == MaterialSpec.user
    ).filter(
        query
    ).with_entities(
        MaterialSpec.id,
        MaterialSpec.name,
        MaterialSpec.description,
        MaterialSpec.create_time,
        MaterialSpec.update_time,
        MaterialSpec.images,
        User.name.label('user')
    ).paginate(page=page, per_page=size)
    return ResultJson.ok(
        data=[dict(
            id=spec.id,
            name=spec.name,
            description=spec.description,
            images=[urljoin(config.HOST, img) for img in spec.images],
            create_time=str(spec.create_time),
            update_time=str(spec.update_time),
            user=spec.user
        ) for spec in specs.items],
        total=specs.total
    )


@material_bp.route('/stocking', methods=['POST'])
@get_params(
    params=['name', 'spec', 'unit', 'amount', 'price', 'warehouseId', 'type', 'code'],
    types=[str, str, str, str, str, str, str, str],
    methods='POST',
    check_para=True
)
@jwt_required()
def stocking_material(name, spec, unit, amount, price, warehouseId, type, code):
    material = Material(
        name=name,
        spec=spec,
        unit=unit,
        total=amount,
        left=amount,
        price=price,
        warehouse_id=warehouseId,
        type=type,
        barcode=code,
        user_id=current_user.id
    )
    material.save()
    MaterialIn(
        material_id=material.id,
        num=amount,
        user_id=current_user.id,
        warehouse_id=warehouseId
    ).save()
    return ResultJson.ok(msg='入库成功！')


@material_bp.route('/list')
@get_params(
    params=['page', 'size', 'name', 'spec', 'warehouse_id'],
    types=[int, int, str, str, str]
)
@jwt_required()
def material_list(page, size, name, spec, warehouse_id):
    query = (Material.id >= 0,)
    if name:
        query += (Material.name.like(f"{name}%"), )
    if spec:
        query += (Material.spec == spec,)
    if warehouse_id:
        query += (Material.warehouse_id == warehouse_id,)
    materials = Material.query.join(
        User,
        User.id == Material.user_id
    ).join(
        Warehouse,
        Warehouse.id == Material.warehouse_id
    ).join(
        MaterialSpec,
        MaterialSpec.id == Material.spec
    ).filter(*query).with_entities(
        Material.id,
        Material.name,
        MaterialSpec.name.label('spec'),
        Material.unit,
        Material.total,
        Material.left,
        Material.used,
        Material.price,
        Material.barcode,
        Material.type,
        Material.create_time,
        Material.update_time,
        User.name.label('user'),
        Warehouse.name.label('warehouse'),
        Material.status
    ).paginate(page=page, per_page=size)
    result = []
    for material in materials.items:

        result.append(dict(
            id=material.id,
            name=material.name,
            spec=material.spec,
            unit=material.unit,
            total=material.total,
            left=material.left,
            price=material.price,
            barcode=material.barcode,
            type=material.type,
            create_time=str(material.create_time),
            update_time=str(material.update_time),
            user=material.user,
            warehouse=material.warehouse,
            used=material.used,
            status=const.MATERIAL_STATUS.get(material.status)
        ))

    return ResultJson.ok(
        data=result,
        total=materials.total
    )
