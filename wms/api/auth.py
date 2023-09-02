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
from wms.models import User
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
