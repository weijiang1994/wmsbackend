"""
# coding:utf-8
@File     :   auth.py
@Time     :   2023/08/11 17:20:18
@Author   :   jiangwei
@Email    :   qq804022023@gmail.com
@Version  :   1.0
@Desc     :   用户登录认证接口
@Software :   Visual Studio Code
@License  :   MIT
"""
from flask import Blueprint, request, jsonify
from wms.models import User, UserRole, Permission
from flask_jwt_extended import (create_access_token, set_access_cookies, jwt_required, current_user, get_jwt_identity,
                                create_refresh_token)
import datetime
from wms.plugins import db, jwt
from wms.utils import ResultJson

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = str(request.json.get('password'))
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(
            code=404,
            msg='用户名或密码错误！',
            success=False
        )
    if not user.check_password(password):
        return jsonify(
            code=404,
            msg='用户名或密码错误！',
            success=False
        )
    user.last_login_time = datetime.datetime.now()
    db.session.commit()
    access_token = create_access_token(identity=user, additional_claims={'admin': True})
    response = jsonify(
        code=200,
        msg='登录成功！',
        userid=user.id,
        username=user.username,
        timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        access_token=access_token,
        refresh_token=create_refresh_token(identity=user),
        success=True
    )
    set_access_cookies(response, access_token)
    return response


@jwt.user_identity_loader
def user_identity_lookup(user):
    if isinstance(user, int):
        return user
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return User.query.filter_by(id=identity).one_or_none()


@auth_bp.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def token_refresh():
    identify = get_jwt_identity()
    if not identify:
        return jsonify(
            code=403,
            msg='无效的Token，请重新登录！'
        )
    # 刷新token后更新用户最后一次登录时间
    user = User.query.filter_by(id=identify if isinstance(identify, int) else identify.id).first()
    user.last_login_time = datetime.datetime.now()
    db.session.commit()
    return jsonify(
        access_token=create_access_token(identity=identify),
        code=200,
        msg='token刷新成功！'
    )


@auth_bp.route('/userInfo')
@jwt_required()
def user_info():
    perms = UserRole.query.join(
        Permission,
        Permission.role == UserRole.role_id
    ).filter(
        UserRole.user_id == current_user.id
    ).with_entities(
        Permission.name
    )
    return ResultJson.ok(
        data=dict(
            id=current_user.id,
            username=current_user.username,
            nickname=current_user.name,
            permissions=[perm.name for perm in perms],
        )
    )
