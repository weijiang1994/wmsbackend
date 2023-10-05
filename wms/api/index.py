"""
coding:utf-8
file: index.py
@time: 2023/9/2 23:46
@desc:
"""
import datetime

from flask import Blueprint, jsonify, request
from wms.models import Warehouse, Material, MaterialOut, MaterialIn, OperateLog, User
from wms.utils import ResultJson, const
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


@index_bp.route('/material/log')
def material_log():
    category = request.args.get('category')
    if category == 'stocking':
        mis = MaterialIn.query.join(
            User,
            User.id == MaterialIn.user_id
        ).join(
            Material,
            Material.id == MaterialIn.material_id
        ).with_entities(
            MaterialIn.num,
            Material.name,
            Material.barcode,
            User.name.label('user'),
            MaterialIn.create_time
        ).order_by(MaterialIn.create_time.desc()).paginate(page=1, per_page=3)
        return ResultJson.ok(
            data=[
                dict(
                    user=mi.user,
                    barcode=mi.barcode,
                    num=mi.num,
                    name=mi.name,
                    create_time=str(mi.create_time),
                    date=str(mi.create_time.date())
                )
                for mi in mis.items
            ]
        )
    if category == 'out':
        mos = MaterialOut.query.join(
            User,
            User.id == MaterialOut.user_id
        ).join(
            Material,
            Material.id == MaterialOut.material_id
        ).with_entities(
            MaterialOut.num,
            Material.name,
            Material.barcode,
            User.name.label('user'),
            MaterialOut.create_time
        ).order_by(MaterialOut.create_time.desc()).paginate(page=1, per_page=3)
        return ResultJson.ok(
            data=[
                dict(
                    user=mo.user,
                    barcode=mo.barcode,
                    num=mo.num,
                    name=mo.name,
                    create_time=str(mo.create_time),
                    date=str(mo.create_time.date())
                )
                for mo in mos.items
            ]
        )
    if category == 'operate':
        ols = OperateLog.query.join(
            User,
            User.id == OperateLog.user_id
        ).with_entities(
            User.name,
            OperateLog.create_time,
            OperateLog.description,
            OperateLog.type
        ).order_by(OperateLog.create_time.desc()).paginate(page=1, per_page=3)
        return ResultJson.ok(
            data=[
                dict(
                    user=ol.name,
                    desc=ol.description,
                    category=const.OPERATE_TYPE.get(ol.type),
                    create_time=str(ol.create_time),
                    date=str(ol.create_time.date())
                )
                for ol in ols.items
            ]
        )


@index_bp.route('/statistics')
def statistics():
    import datetime
    date_range = request.args.get('range')
    until = datetime.date.today()
    start = datetime.timedelta(days=-7) + until

    def get_date_count(start, until, table):
        counts = table.query.filter(
            func.DATE(table.create_time) >= start,
            func.DATE(table.create_time) <= until
        ).group_by(
            func.DATE(table.create_time)
        ).with_entities(
            func.DATE(table.create_time).label('date'),
            func.COUNT(table.create_time).label('count')
        ).all()
        return counts

    if date_range == 'week':
        mi_counts = get_date_count(start, until, MaterialIn)
        mo_counts = get_date_count(start, until, MaterialOut)
    elif date_range == 'half':
        start = datetime.timedelta(days=-15) + until
        mi_counts = get_date_count(start, until, MaterialIn)
        mo_counts = get_date_count(start, until, MaterialOut)
    else:
        start = datetime.timedelta(days=-30) + until
        mi_counts = get_date_count(start, until, MaterialIn)
        mo_counts = get_date_count(start, until, MaterialOut)
    mi_dict = {str(mi.date): mi.count for mi in mi_counts}
    mo_dict = {str(mo.date): mo.count for mo in mo_counts}
    date_ranges = [str(start + datetime.timedelta(days=i)) for i in range((until - start).days + 1)]
    mi_series = {'areaStyle': {'normal': {}}, 'data': [], 'name': "入库", 'stack': '总量', 'type': 'line'}
    mo_series = {'areaStyle': {'normal': {}}, 'data': [], 'name': "出库", 'stack': '总量', 'type': 'line'}
    for dr in date_ranges:
        if dr not in mi_dict:
            mi_series['data'].append(0)
        else:
            mi_series['data'].append(mi_dict[dr])
        if dr not in mo_dict:
            mo_series['data'].append(0)
        else:
            mo_series['data'].append(mo_dict[dr])

    return ResultJson.ok(series=[mi_series, mo_series], dates=date_ranges)
