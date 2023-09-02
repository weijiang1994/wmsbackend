'''
# coding:utf-8
@File     :   decorators.py
@Time     :   2023/08/11 17:24:48
@Author   :   jiangwei 
@Email    :   qq804022023@gmail.com 
@Version  :   1.0
@Desc     :   一些常用的装饰器
@Software :   Visual Studio Code
@License  :   MIT
'''
from functools import wraps
from flask import jsonify, request


def get_params(
        params: list,
        types: list = [],
        methods: str = 'GET',
        check_para: bool = False,
        remove_none: bool = False,
        is_kwargs: bool = False
):
    """
    获取请求中的参数
    :param remove_none: 是否移除值为空的参数
    :param check_para: 是否检查参数完整
    :param params: 参数列表
    :param types: 参数类型
    :param methods: 请求方法
    :param is_kwargs: 是否传递为关键字参数
    :return: 参数列表所对应的参数值
    """

    # TODO 可以直接修改为关键字参数，由于引用的地方太多，后续有空了再改
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg = []
            kwarg = {}
            if methods == 'GET':
                if len(types) != len(params):
                    types.append()
                for param, type in zip(params, types):
                    # 对于bool类型的参数特殊处理，因为如果传入的为false也会当做为True
                    if type == bool:
                        if request.args.get(param, default='false').lower() == 'true':
                            arg.append(True)
                            kwarg[param] = True
                        else:
                            arg.append(False)
                            kwarg[param] = False
                    else:
                        value = request.args.get(param, type=type)
                        arg.append(value)
                        kwarg[param] = value
            elif methods == 'POST':
                for param in params:
                    arg.append(request.json.get(param))
            if check_para:
                if None in arg or '' in arg:
                    return jsonify(dict(
                        code=403,
                        msg='参数不完整,请检查参数后重试!'
                    ))
            if remove_none:
                arg = list(filter(lambda x: x, arg))
                kwarg = dict(filter(lambda x: x[1] not in [
                             None, ''], kwarg.items()))
            if is_kwargs:
                return func(**kwarg)
            return func(*arg)

        return wrapper

    return decorator
