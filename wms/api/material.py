"""
coding:utf-8
file: material.py
@time: 2023/9/17 23:36
@desc:
"""
from flask import Blueprint, request
from wms.decorators import get_params

material_bp = Blueprint('material_bp', __name__, url_prefix='/material')
