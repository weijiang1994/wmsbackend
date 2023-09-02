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


class User(db.Model, TimeMixin):
    __tablename__ = 't_user'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, comment='用户ID')
    username = db.Column(db.String(32), unique=True,
                         nullable=False, comment='用户名')
    password = db.Column(db.String(128), nullable=False, comment='密码')
    email = db.Column(db.String(32), unique=True, nullable=False, comment='邮箱')
    phone = db.Column(db.String(11), unique=True,
                      nullable=False, comment='手机号')

    def __repr__(self):
        return '<User %r>' % self.username


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
    name = db.Column(db.String(32), unique=True, nullable=False, comment='权限名')
    role = db.Column(db.INTEGER, comment='角色ID')
    description = db.Column(db.String(128), nullable=False, comment='角色描述', default='')

    def __repr__(self):
        return '<Permission %r>' % self.name


class Warehouse(db.Model, TimeMixin):
    __tablename__ = 't_warehouse'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, comment='仓库ID')
    name = db.Column(db.String(32), unique=True, nullable=False, comment='仓库名')
    volunm = db.Column(db.Integer, comment='仓库容量')
    address = db.Column(db.String(128), comment='仓库地址')
    manager = db.Column(db.String(32), comment='仓库管理员')
    status = db.Column(db.Integer, comment='仓库状态')
    left = db.Column(db.Integer, comment='仓库剩余容量')
