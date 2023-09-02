'''
# coding:utf-8
@File     :   plugins.py
@Time     :   2023/08/11 17:42:29
@Author   :   jiangwei 
@Email    :   qq804022023@gmail.com 
@Version  :   1.0
@Desc     :   一些第三方插件
@Software :   Visual Studio Code
@License  :   MIT
'''
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()


def register_extensions(app):
    db.init_app(app)
    db.app = app
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db=db)
