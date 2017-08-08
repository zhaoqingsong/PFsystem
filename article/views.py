from flask import request,render_template,redirect,url_for,views
from flask import Blueprint
from flask.views import MethodView,View
article = Blueprint('article',__name__)

#基于BLUEPRINT 的方式
# @article.route('/articles/')
# def article_list():
#     return render_template('article-list.html')
#
# @article.route('/articles/<id>/')
# def artile_detail(id=None):
#     item = {'id': id}
#     return render_template('articles-detail.html', item=item)

class ArticleListView(MethodView):
    def get(self):
        return render_template('article-list.html')
    def post(self):
        pass

class ArticleDetailView(MethodView):
    def get(self, id=None):
        item = {'id': id}
        return render_template('articles-detail.html', item=item)

article.add_url_rule('/articles/', view_func=ArticleListView.as_view('article_list'))
article.add_url_rule('/article/<int:id>/', view_func=ArticleDetailView.as_view('article_detail'))