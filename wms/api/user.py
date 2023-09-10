"""
coding:utf-8
file: user.py.py
@time: 2023/9/7 23:53
@desc:
"""
from flask import Blueprint, request
from wms.utils import ResultJson
from wms.models import User, Permission, Role, UserRole
from wms.decorators import get_params
from sqlalchemy.sql.expression import or_
from wms.plugins import db
from flask_jwt_extended import jwt_required

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


@user_bp.route('/list')
@jwt_required()
def user_list():
    users = User.query.with_entities(
        User.id,
        User.username,
        User.name,
        User.phone,
        User.email,
        User.last_login_time,
        User.status
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
            last_login=str(user.last_login_time),
            status=user.status
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
@jwt_required()
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


@user_bp.route('/status', methods=['POST'])
@get_params(
    params=['uid', 'status'],
    types=[int, int],
    methods='POST'
)
@jwt_required()
def change_status(uid, status):
    user = User.query.filter_by(id=uid).first()
    if not user:
        return ResultJson.forbidden(msg='用户不存在！')
    user.status = status
    db.session.commit()
    return ResultJson.ok(msg='修改成功！')


@user_bp.route('/permission/list')
@jwt_required()
def perm_list():
    if request.args.get('type') == 'brief':
        return ResultJson.ok(data=[
            perm.name for perm in Permission.query.group_by(Permission.name).with_entities(Permission.name).all()
        ])
    permissions = Permission.query.join(
        Role,
        Role.id == Permission.role
    ).with_entities(
        Permission.id,
        Permission.name,
        Permission.description,
        Role.name.label("role")
    ).all()
    perms = {}
    for perm in permissions:
        if perm.name not in perms.keys():
            perms[perm.name] = dict(
                id=perm.id,
                name=perm.name,
                desc=perm.description,
                roles=[]
            )
        if perm.role not in perms[perm.name]['roles']:
            perms[perm.name]['roles'].append(perm.role)
    return ResultJson.ok(data=list(perms.values()))


@user_bp.route('/permission/add', methods=['POST'])
@get_params(
    params=['name', 'desc', 'roles'],
    types=[str, str, list],
    methods='POST'
)
@jwt_required()
def add_perm(name, desc, roles):
    for role in roles:
        r = Role.query.filter_by(name=role).first()
        if not r:
            continue
        if Permission.query.filter(Permission.name == name, Permission.role == r.id).first():
            continue
        db.session.add(Permission(name=name, description=desc, role=r.id))
    db.session.commit()
    return ResultJson.ok(msg='权限添加成功！')


@user_bp.route('/permission/edit', methods=['POST'])
@get_params(
    params=['old_name', 'name', 'desc', 'roles'],
    types=[int, str, str, list],
    methods='POST'
)
@jwt_required()
def perm_edit(old_name, name, desc, roles):
    Permission.query.filter_by(name=old_name).delete()
    roles = Role.query.filter(Role.name.in_(roles)).all()
    for role in roles:
        perm = Permission(name=name, role=role.id, description=desc)
        db.session.add(perm)
    db.session.commit()
    return ResultJson.ok(msg='修改成功！')


@user_bp.route('/permission/delete', methods=['POST'])
@jwt_required()
def delete_perm():
    perm_name = request.json.get('name')
    Permission.query.filter_by(name=perm_name).delete()
    db.session.commit()
    return ResultJson.ok(msg='删除成功！')


@user_bp.route('/role/lists')
@jwt_required()
def role_detail_list():
    roles = Role.query.join(
        Permission,
        Permission.role == Role.id
    ).with_entities(
        Permission.name.label('perm'),
        Role.name,
        Role.id,
        Role.description
    )
    results = {}
    for role in roles:
        if role.name not in results.keys():
            results[role.name] = dict(
                name=role.name,
                id=role.id,
                desc=role.description,
                perms=[]
            )
        results[role.name]['perms'].append(role.perm)
    return ResultJson.ok(
        data=list(results.values())
    )


@user_bp.route('/role/add', methods=['POST'])
@jwt_required()
@get_params(
    params=['name', 'desc', 'perms'],
    types=[str, str, list],
    methods='POST'
)
def add_role(name, desc, perms):
    if Role.query.filter(Role.name == name).first():
        return ResultJson.forbidden(msg='角色已经存在')
    role = Role(
        name=name,
        description=desc
    )
    db.session.add(role)
    db.session.commit()
    add_new_perm4role(perms, role)
    db.session.commit()
    return ResultJson.ok(msg='添加角色成功！')


def add_new_perm4role(perms: list, role: Role) -> None:
    """
    给角色添加权限

    :param perms: 权限名称列表
    :param role: 角色
    :return: None
    """
    for perm in perms:
        db_perm = Permission.query.filter(Permission.name == perm).first()
        p = Permission(
            name=perm,
            role=role.id,
            description=db_perm.description if db_perm else ''
        )
        db.session.add(p)
    db.session.commit()


@user_bp.route('/role/edit', methods=['POST'])
@jwt_required()
@get_params(
    params=['rid', 'name', 'desc', 'perms'],
    types=[int, str, str, list],
    methods='POST'
)
def edit_role(rid, name, desc, perms):
    role = Role.query.filter(Role.id == rid).first()
    if not role:
        return ResultJson.forbidden(msg='不存在的角色！')
    # 删除原有的权限
    role.name = name
    role.description = desc
    Permission.query.filter(Permission.role == rid).delete()
    db.session.commit()
    add_new_perm4role(perms, role)
    return ResultJson.ok(msg='角色信息编辑成功！')
