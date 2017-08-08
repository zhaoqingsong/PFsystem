import sqlite3
import os

from flask import Flask,render_template,redirect,url_for,make_response
from flask import request,g,flash,send_from_directory,session
from datetime import datetime,timedelta
from account.views import Reguser,MyRegUser,UserLogin
from sqlmap.sqljob import connect_db,execute_db,query_db
from article.views import article
from product.views import product

app = Flask(__name__)
app.debug = True
app.secret_key = "＃0m@da23/\d%$8ebe2^%$#sada*@%$!"

UPLOAD_FOLDER = r'./uploads/'
ALLOWED_EXTENSIONS = ['.jpg','.png','.gif']
DATABASE_URL = r'./db/feedback.db'
#检查文件是否允许上传
def allowed_file(filename):
    _, ext = os.path.splitext(filename)   #splitext可以实现文件名和后缀分离，_表示忽略名字
    return ext.lower() in ALLOWED_EXTENSIONS

conn = sqlite3.connect(DATABASE_URL,check_same_thread=False)
c = conn.cursor()

# 将游标获取的Tuple 根据数据库列表转换为DICT
def make_dicts(cursor,row):
    return dict( (cursor.description[i][0],value) for i,value in enumerate(row))

# # 建立数据库连接
# def get_db():
#     db = getattr(g,'_database',None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE_URL)
#         db.row_factory = make_dicts
#     return db
#
# # 执行SQL语句不返回数据结果
# def execute_sql(sql,prms=()):
#     c = get_db().cursor()
#     c.execute(sql, prms)
#     c.connection.commit()
#
# # 执行用于选择数据的SQL语句
# def query_sql(sql, prms=(), one=False):
#     c = get_db().cursor()
#     result = c.execute(sql, prms).fetchall()
#     c.close()
#     return (result[0] if result else None) if one else result


#关闭连接（在当前app 上下文销毁时关闭连接）
@app.teardown_appcontext
def close_connection(exeption):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

app.register_blueprint(article)
app.register_blueprint(product, url_prefix='/pro')

@app.route('/')
def pfs():
    return render_template('base.html')
@app.route('/profile/<filename>/')
def render_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# @app.route('/login/',methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         pass_salt = "124%wer0514"
#         pwd = request.form.get('pwd')
#         md5 = hashlib.md5()
#         md5.update("{}{}{}".format(pwd,username,pass_salt).encode('utf-8'))
#         md5_pass = md5.hexdigest()
#         #return "{}{}".format(pwd,username).encode('utf-8')
#         #return md5_pass
#         sql = 'select count(*) as [Count] from UserInfo where UserName = ? and Password = ?;'
#         result = query_sql(sql,(username,md5_pass),one=True)
#
#         if int(result.get('Count')) > 0:
#             session['adminuser'] = username
#             return redirect(url_for('feedback_list'))
#         flash('用户名或者密码不匹配,请重新输入!')
#
#     return render_template('login.html')
    #return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    if session.get('adminuser'):
        session.pop('adminuser')
    return redirect(url_for('feedback_list'))

@app.route('/feedback/')
def feedback():
    if session.get('adminuser',None) is None:
        return redirect(url_for('login'))
    else:
        sql = 'select ROWID,CategoryName from category'
        categories = query_db.query_sql(sql)
        return render_template('post.html',categories=categories)

@app.route('/post_feedback/',methods=['POST'])
def post_feedback():
    #获取表单指
    if request.method == 'POST':
        subject = request.form['subject']
        categoryid = request.form.get('category',1)
        username = request.form.get('username')
        email = request.form.get('email')
        body = request.form.get('body')
        releasetime = datetime.now()
        state = 0
        img_path = None

        #if 'screenshot' in request.files:
        if request.files.get('screenshot',None):
            # 获取图片上传，并且获取文件名，以便和其它字段一并插入数据表
            img = request.files['screenshot']
            if img and allowed_file(img.filename):
                img_path = datetime.now().strftime('%Y%m%d%H%M%f') + os.path.splitext(img.filename)[1]
                img.save(os.path.join(UPLOAD_FOLDER, img_path))

        sql = "insert into feedback (Subject, CategoryID, UserName, Email, Body, State, ReleaseTime,Image) values (?,?,?,?,?,?,?,?)"
        execute_db.execute_sql(sql,(subject,categoryid,username,email,body,state,releasetime,img_path))
        return redirect(url_for('feedback'))

@app.route('/admin/list/')
def feedback_list():
    if session.get('adminuser', None) is None:
        return redirect(url_for('login'))
    else:
        key = request.args.get('key','')
        sql = 'select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c on c.ROWID = f.CategoryID WHERE f.Subject LIKE ? ORDER BY f.ROWID DESC '
        feedbacks = query_db.query_sql(sql,('%{}%'.format(key),))
        return render_template('feedback-list.html',items=feedbacks)

@app.route('/admin/edit/<id>/')
def edit_feedback(id=None):
    if session.get('adminuser', None) is None:
        return redirect(url_for('login'))
    else:
        sql = 'select ROWID,CategoryName from category'
        categories = query_db.query_sql(sql)
        #获取当前ID的信息并绑定至form表单，以备修改
        sql = 'select rowid,* from feedback WHERE rowid = ?'
        current_feedback = query_db.query_sql(sql,(id,), one=True)
        return render_template('edit.html', categories=categories,item=current_feedback)

@app.route('/admin/save_edit/',methods=['POST'])
def save_feedback():
    if request.method == 'POST':
        #获取表单
        rowid = request.form.get('rowid',None)
        reply = request.form.get('reply')
        is_processed = 1 if request.form.get('is_processed',0) == 'on' else 0
        sql = 'update feedback set Reply = ?,State = ? WHERE rowid = ?'
        execute_db.execute_sql(sql,(reply,is_processed,rowid))
        return redirect(url_for('feedback_list'))
        #return str(is_processed)
@app.route('/admin/feedback/del/<id>/')
def delete_feedback(id=0):
    if session.get('adminuser',None) is None:
        return redirect(url_for('login'))
    else:
        sql = "delete from feedback WHERE ROWID = ?"
        execute_db.execute_sql(sql,(id,))
        return redirect(url_for('feedback_list'))
@app.route('/setck/')
def set_mycookie():
    resp = make_response('ok')
    resp.set_cookie('username','',path='/', expires=datetime.now() + timedelta(days=7))
    return resp

@app.route('/getck/')
def get_mycookie():
    ck = request.cookies.get('username',None)
    if ck:
        return ck
    return '未找到'

@app.route('/rmck/')
def remove_cookie():
    resp = make_response('删除Cookie')
    resp.set_cookie('username','',expires=datetime.now() + timedelta(days=-1))
    return resp

app.add_url_rule('/login/',view_func=UserLogin.as_view('login'))
#app.add_url_rule('/reg/',view_func=Reguser.as_view('reg_user'))
app.add_url_rule('/reg/',view_func=MyRegUser.as_view('reg_user'))

if __name__ == '__main__':
    app.run()