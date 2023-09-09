"""
coding:utf-8
file: user.py.py
@time: 2023/9/7 23:53
@desc:
"""
from flask import Blueprint
from wms.utils import ResultJson
from wms.models import User, Permission, Role, UserRole
from wms.decorators import get_params
from sqlalchemy.sql.expression import or_
from wms.plugins import db

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


@user_bp.route('/list')
def user_list():
    users = User.query.with_entities(
        User.id,
        User.username,
        User.name,
        User.phone,
        User.email,
        User.last_login_time
    ).all()
    results = []
    for user in users:
        roles = UserRole.query.join(
            Role,
            Role.id == UserRole.role_id
        ).filter(UserRole.user_id == user.id).with_entities(
            Role.id,
            Role.name,
            Role.description
        ).all()
        results.append(dict(
            roles=[dict(
                name=role.name,
                id=role.id,
                desc=role.description
            ) for role in roles],
            username=user.username,
            name=user.name,
            id=user.id,
            email=user.email,
            phone=user.phone,
            last_login=str(user.last_login_time)
        ))
    return ResultJson.ok(data=results)


@user_bp.route('/role/list')
def role_list():
    return ResultJson.ok(data=dict(
        roles=[dict(id=role.id, name=role.name, desc=role.description) for role in Role.query.all()])
    )


@user_bp.route('/add', methods=['POST'])
@get_params(
    params=['username', 'name', 'email', 'phone', 'password', 'roles'],
    types=[str, str, str, str, str, list],
    methods='POST'
)
def add_user(username, name, email, phone, password, roles):
    print(username, name, email, phone, password, roles)
    if User.query.filter(or_(
            User.username == username,
            User.email == email
    )).first():
        return ResultJson.forbidden(msg='用户名或邮箱已经被使用！')
    user = User(
        username=username,
        name=name,
        email=email,
        phone=phone
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    db_roles = Role.query.filter(Role.name.in_(roles)).all()
    for role in db_roles:
        db.session.add(UserRole(user_id=user.id, role_id=role.id))
    db.session.commit()
    return ResultJson.ok(
        data=dict(
            username=username,
            name=name,
            email=email,
            phone=phone,
            roles=[dict(name=role) for role in roles]
        )
    )
