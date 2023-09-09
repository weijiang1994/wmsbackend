"""
# coding:utf-8
@File     :   __init__.py
@Time     :   2023/08/11 17:20:00
@Author   :   jiangwei
@Email    :   qq804022023@gmail.com
@Version  :   1.0
@Desc     :   后端服务入口
@Software :   Visual Studio Code
@License  :   MIT
"""
from flask import Flask
from wms.api.auth import auth_bp
from wms.api.index import index_bp
from wms.api.user import user_bp
from wms.plugins import register_extensions
from wms.settings import DevelopmentConfig, ProductionConfig
from wms.models import *
from wms.plugins import db


def create_app(config_name=None):
    app = Flask(__name__)
    if config_name:
        app.config.from_object(app_configuration.get(config_name))
    else:
        app.config.from_object(ProductionConfig)
    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp)
    register_extensions(app=app)
    register_commands(app)

    @app.route('/')
    def index():
        return 'Welcome to WMS!'

    return app


def register_commands(app: Flask):
    import click

    @app.cli.command('init', help='Initialize the database.')
    @click.option('--drop', is_flag=True, help='Drop the database first.')
    def init_db(drop):
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command('create-admin', help='Create the admin user.')
    @click.option('--username', prompt=True, help='The username of the admin user.')
    @click.option('--email', prompt=True, help='The email of the admin user.')
    @click.option('--name', prompt=True, help='The email of the admin user.')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
                  help='The password of the admin user.')
    def create_admin(username, password, email, name):
        sys_admin = Role.query.filter_by(name='sys-admin').first()
        if not sys_admin:
            click.echo('The system administrator permission does not exist.')
            return
        if User.query.filter_by(username=username).first():
            click.echo('The username is already in use.')
            return
        if User.query.filter_by(email=email).first():
            click.echo('The email is already in use.')
            return

        user = User(username=username, email=email, phone='', name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        ur = UserRole(user_id=user.id, role_id=sys_admin.id)
        db.session.add(ur)
        db.session.commit()
        click.echo('Created admin user.')

    @app.cli.command('init-perm', help='Initialize the permission.')
    def init_perm():
        if Role.query.filter_by(name='sys-admin').first():
            click.echo('The permission is already initialized.')
            return
        role = Role(name='sys-admin', description='系统管理员，拥有所有权限，最高权限角色。')
        db.session.add(role)
        db.session.commit()
        permissions = [
            ['sys-admin', '系统管理员，最高权限'],
            ['user-admin', '用户管理员，可以增加、编辑用户以及用户权限'],
            ['site-user', '网站用户，最低级权限每个用户都拥有'],
            ['out-admin', '物料出库权限'],
            ['in-admin', '物料入库权限']
        ]
        for perm in permissions:
            permission = Permission(name=perm[0], role=role.id, description=perm[1])
            db.session.add(permission)
        db.session.commit()
        click.echo('Initialized permission.')
