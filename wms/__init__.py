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
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
                  help='The password of the admin user.')
    def create_admin(username, password):
        if User.query.filter_by(username=username).first():
            click.echo('The username is already in use.')
            return
        User(username=username)
        db.create_admin(username, password)
        click.echo('Created admin user.')

    def init_permission():
        from wms.models import Permission
        Permission.init_permission()

    @app.cli.command('init-permission', help='Initialize the permission.')
    def init_permission():
        init_permission()
        click.echo('Initialized permission.')

    @app.cli.command('init-perm', help='Initialize the permission.')
    def init_perm():
        if Role.query.filter_by(name='sys-admin').first():
            click.echo('The permission is already initialized.')
            return
        role = Role(name='sys-admin', description='System administrator.')
        db.session.add(role)
        db.session.commit()
        permissions = ['sys-admin', 'user-admin']
        for perm in permissions:
            permission = Permission(name=perm, role=role.id, description='')
            db.session.add(permission)
        db.session.commit()
        click.echo('Initialized permission.')
