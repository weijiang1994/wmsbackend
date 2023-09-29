"""
# coding:utf-8
@File     :   models.py
@Time     :   2023/08/11 17:45:59
@Author   :   jiangwei
@Email    :   qq804022023@gmail.com
@Version  :   1.0
@Desc     :   models.py
@Software :   Visual Studio Code
@License  :   MIT
"""
from wms.plugins import db
from sqlalchemy.ext.declarative import declared_attr
import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class TimeMixin:
    @declared_attr
    def create_time(self):
        return db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')

    @declared_attr
    def update_time(self):
        return db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='最后一次更新时间')

    @classmethod
    def update_or_insert(cls, condition: tuple, **kwargs):
        """
        更新已有数据或者插入新的数据

        :param condition: 查询条件
        :param kwargs: 需要更新或者插入的字段
        :return: 类实例对象
        """
        existed = cls.query.filter(*condition)
        if existed.first():
            existed.update(kwargs)
            existed = existed.first()
        else:
            existed = cls(**kwargs)
            db.session.add(existed)
        db.session.commit()
        return existed

    @classmethod
    def existed(cls, condition: tuple):
        return cls.query.filter(*condition).first()

    def save(self):
        db.session.add(self)
        db.session.commit()


class User(db.Model, TimeMixin):
    __tablename__ = 't_user'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, comment='用户ID')
    username = db.Column(db.String(32), unique=True,
                         nullable=False, comment='用户名')
    name = db.Column(db.String(32), nullable=False, comment='姓名', default='')
    password = db.Column(db.String(128), nullable=False, comment='密码')
    email = db.Column(db.String(32), unique=True, nullable=False, comment='邮箱')
    phone = db.Column(db.String(11), default='', nullable=False, comment='手机号')
    last_login_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='最后登录时间')
    status = db.Column(db.Integer, default=1, comment='状态：0-禁用，1-启用')
    avatar = db.Column(db.String(1024), default='/static/default.png', comment='用户头像')

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)


class Role(db.Model, TimeMixin):
    __tablename__ = 't_role'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, comment='角色ID')
    name = db.Column(db.String(32), unique=True, nullable=False, comment='角色名')
    description = db.Column(db.String(128), nullable=False, comment='角色描述', default='')

    def __repr__(self):
        return '<Role %r>' % self.name


class UserRole(db.Model, TimeMixin):
    __tablename__ = 't_user_role'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, comment='用户角色ID')
    user_id = db.Column(db.Integer, comment='用户ID')
    role_id = db.Column(db.Integer, comment='角色ID')

    def __repr__(self):
        return '<UserRole %r>' % self.id


class Permission(db.Model, TimeMixin):
    __tablename__ = 't_permission'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, comment='权限ID')
    name = db.Column(db.String(32), nullable=False, comment='权限名')
    role = db.Column(db.INTEGER, comment='角色ID')
    description = db.Column(db.String(128), nullable=False, comment='角色描述', default='')

    def __repr__(self):
        return '<Permission %r>' % self.name


class Warehouse(db.Model, TimeMixin):
    __tablename__ = 't_warehouse'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, comment='仓库ID')
    name = db.Column(db.String(32), unique=True, nullable=False, comment='仓库名')
    volume = db.Column(db.Integer, default=0, comment='仓库容量')
    address = db.Column(db.String(128), default='', comment='仓库地址')
    manager = db.Column(db.String(32), default=0, comment='仓库管理员')
    status = db.Column(db.Integer, default=1, comment='仓库状态')
    left = db.Column(db.Integer, default=0, comment='仓库剩余容量')
    tag = db.Column(db.JSON, default=[], comment='仓库标签')


class Material(db.Model, TimeMixin):
    __tablename__ = 't_material'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='物料ID')
    name = db.Column(db.String(512), unique=True, nullable=False, comment='物料名')
    type = db.Column(db.String(32), default='produce', comment='物料类型')
    unit = db.Column(db.String(32), default='个', comment='物料单位')
    price = db.Column(db.Float, default=0, comment='物料单价')
    status = db.Column(db.Integer, default=0, comment='物料状态')
    total = db.Column(db.Integer, default=0, comment='物料总数量')
    left = db.Column(db.Integer, default=0, comment='物料剩余数量')
    barcode = db.Column(db.String(128), comment='条形码编号')
    warehouse_id = db.Column(db.Integer, comment='仓库ID', default=0)
    user_id = db.Column(db.Integer, comment='用户ID', default=0)
    used = db.Column(db.Integer, default=0, comment='物料已使用数量')
    spec = db.Column(db.Integer, default=0, comment='物料规格')


class MaterialOut(db.Model, TimeMixin):
    __tablename__ = 't_material_out'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='物料出库ID')
    material_id = db.Column(db.Integer, default=0, comment='物料ID')
    user_id = db.Column(db.Integer, default=0, comment='出库人')
    warehouse_id = db.Column(db.Integer, comment='仓库ID', default=0)
    num = db.Column(db.Integer, default=0, comment='出库数量')
    reason = db.Column(db.String(512), default='', comment='出库原因')


class MaterialIn(db.Model, TimeMixin):
    __tablename__ = 't_material_in'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='物料入库ID')
    material_id = db.Column(db.Integer, default=0, comment='物料ID')
    user_id = db.Column(db.Integer, default=0, comment='入库人')
    warehouse_id = db.Column(db.Integer, comment='仓库ID', default=0)
    num = db.Column(db.Integer, default=0, comment='入库数量')
    in_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='入库时间')


class MaterialSpec(db.Model, TimeMixin):
    __tablename__ = 't_material_spec'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='物料入库ID')
    name = db.Column(db.String(512), default='', comment='规格名称')
    description = db.Column(db.TEXT, default='', comment='规格描述信息')
    images = db.Column(db.JSON, default='', comment='规格简图')
    user = db.Column(db.INTEGER, default=0, comment='规格创建人')

