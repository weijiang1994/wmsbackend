"""
# coding:utf-8
@File     :   settings.py
@Time     :   2023/08/11 17:44:15
@Author   :   jiangwei
@Email    :   qq804022023@gmail.com
@Version  :   1.0
@Desc     :   settings.py
@Software :   Visual Studio Code
@License  :   MIT
"""
from dotenv import load_dotenv
import os
import sys
import datetime

if sys.platform.startswith('win'):
    sqlite_pre = 'sqlite:///'
else:
    sqlite_pre = 'sqlite:////'

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# 手动加载env文件,防止部署到服务器时不主动加载env获取不到服务器启动的关键参数
load_dotenv('.env')


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY')

    PER_PAGE = 20
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SCHEDULER_API_ENABLED = True

    # database config
    DATABASE_USER = os.getenv('DATABASE_USERNAME')
    DATABASE_PWD = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST = os.getenv('DATABASE_HOST')
    DATABASE_PORT = os.getenv('DATABASE_PORT')
    DATABASE_NAME = os.getenv('DATABASE_NAME')

    # mail config
    MAIL_SUBJECT_PRE = '[openKylin-dashboard]'
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('openKylin-Dashboard', MAIL_USERNAME)

    # celery config
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # jwt config
    JWT_SECRET_KEY = 'a3e847bc-5707-11ec-9608-9f9d60f7ad70'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['cookies', 'headers', 'json', 'query_string']
    JWT_HEADER_NAME = 'Access-Token'
    JWT_ACCESS_COOKIE_NAME = 'Access-Token'
    JWT_QUERY_STRING_NAME = 'access_token'
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=15)


class DevelopmentConfig(BaseConfig):
    if BaseConfig.DATABASE_USER is not None:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(BaseConfig.DATABASE_USER,
                                                                                          BaseConfig.DATABASE_PWD,
                                                                                          BaseConfig.DATABASE_HOST,
                                                                                          BaseConfig.DATABASE_PORT,
                                                                                          BaseConfig.DATABASE_NAME)
    else:
        SQLALCHEMY_DATABASE_URI = sqlite_pre + os.path.join(basedir, 'data.db')
    REDIS_URL = "redis://localhost:6379"


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(BaseConfig.DATABASE_USER,
                                                                                      BaseConfig.DATABASE_PWD,
                                                                                      BaseConfig.DATABASE_HOST,
                                                                                      BaseConfig.DATABASE_PORT,
                                                                                      BaseConfig.DATABASE_NAME)
    REDIS_URL = "redis://localhost:6379"


class TestConfig(BaseConfig):
    SQLALCHEMY_ECHO = True
    REDIS_URL = "redis://localhost:6379"


app_configuration = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestConfig
}
