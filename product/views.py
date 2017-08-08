from flask import request,render_template,redirect,url_for
from flask import Blueprint
from flask.views import MethodView,View
product = Blueprint('product',__name__)

@product.route('/')
def product_list():
    return '产品列表'

@product.route('<int:id>')
def product_detail(id=None):
    return