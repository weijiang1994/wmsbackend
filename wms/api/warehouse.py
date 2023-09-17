"""
coding:utf-8
file: Warehouse.py
@time: 2023/9/10 23:18
@desc:
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from wms.models import Warehouse, User
from wms.decorators import get_params
from wms.plugins import db
from wms.utils import ResultJson
from urllib.parse import urljoin
import os

warehouse_bp = Blueprint('warehouse_bp', __name__, url_prefix='/warehouse')


@warehouse_bp.route("/add", methods=['POST'])
@jwt_required()
@get_params(
    params=['name', 'address', 'manager', 'volume', 'tags'],
    types=[str, str, int, int, list],
    methods='POST'
)
def add(name, address, manager, volume, tags):
    wh = Warehouse(
        name=name,
        address=address,
        manager=manager,
        volume=volume,
        left=volume,
        tag=tags or []
    )
    db.session.add(wh)
    db.session.commit()
    return ResultJson.ok(msg='添加仓库成功！')


@warehouse_bp.route("/list")
@jwt_required()
def lists():
    warehouses = Warehouse.query.join(
        User,
        User.id == Warehouse.manager
    ).with_entities(
        Warehouse.id,
        Warehouse.name,
        Warehouse.address,
        Warehouse.tag,
        Warehouse.volume,
        Warehouse.left,
        Warehouse.status,
        Warehouse.create_time,
        User.username,
        User.name.label('uname'),
        User.id.label('uid'),
        User.avatar
    ).all()
    return ResultJson.ok(data=[dict(
        id=wh.id,
        name=wh.name,
        address=wh.address,
        tags=wh.tag,
        volume=wh.volume,
        left=wh.left,
        status=wh.status,
        create_time=str(wh.create_time),
        manager=dict(
            username=wh.username,
            name=wh.uname,
            avatar=urljoin(os.environ.get('HOST'), wh.avatar)
        )
    ) for wh in warehouses])
