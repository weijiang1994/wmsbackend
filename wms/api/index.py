"""
coding:utf-8
file: index.py
@time: 2023/9/2 23:46
@desc:
"""
import datetime

from flask import Blueprint, jsonify
from wms.models import Warehouse, Material, MaterialOut, MaterialIn
from wms.utils import ResultJson
from sqlalchemy.sql.expression import func

index_bp = Blueprint("index_bp", __name__)


@index_bp.route("/warehouse")
def warehouse():
    count = Warehouse.query.count()
    return ResultJson.ok(data=dict(
        count=count,
        rooter='存储物料仓库总数',
        title='仓库统计'
    ))


@index_bp.route('/material')
def material():
    count = Warehouse.query.count()
    return ResultJson.ok(data=dict(
        count=count,
        rooter='已存储物料总数',
        title='物料统计'
    ))


@index_bp.route('/material/<category>')
def material_category(category):
    if category == 'out':
        count = MaterialOut.query.filter(func.DATE(MaterialOut.create_time) == datetime.date.today()).count()
        return ResultJson.ok(data=dict(
            count=count,
            rooter='今日出库物料总数',
            title='物料出库统计'
        ))
    if category == 'in':
        count = MaterialIn.query.filter(func.DATE(MaterialIn.create_time) == datetime.date.today()).count()
        return ResultJson.ok(data=dict(
            count=count,
            rooter='今日入库物料总数',
            title='物料入库统计'
        ))
    return ResultJson.not_found()
