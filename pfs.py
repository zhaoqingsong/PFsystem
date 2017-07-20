import sqlite3
from flask import Flask,render_template,redirect,url_for,request,g
from datetime import datetime

DATABASE_URL = r'./db/feedback.db'
app = Flask(__name__)
app.debug = True

conn = sqlite3.connect(DATABASE_URL,check_same_thread=False)
c = conn.cursor()

# 将游标获取的Tuple 根据数据库列表转换为DICT
def make_dicts(cursor,row):
    return dict( (cursor.description[i][0],value) for i,value in enumerate(row))

# 建立数据库连接
def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_URL)
        db.row_factory = make_dicts
    return db

# 执行SQL语句不返回数据结果
def execute_sql(sql,prms=()):
    c = get_db().cursor()
    c.execute(sql, prms)
    c.connection.commit()

# 执行用于选择数据的SQL语句
def query_sql(sql, prms=(), one=False):
    c = get_db().cursor()
    result = c.execute(sql, prms).fetchall()
    c.close()
    return (result[0] if result else None) if one else result

#关闭连接（在当前app 上下文销毁时关闭连接）
@app.teardown_appcontext
def close_connection(exeption):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def pfs():
    return render_template('base.html')

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        sql = 'select count(*) as [Count] from UserInfo where UserName = ? and Password = ?;'
        result = query_sql(sql,(username,pwd),one=True)
        if int(result.get('Count')) > 0:
            return redirect(url_for('feedback_list'))
        return '用户名或者密码不匹配！'
    return render_template('login.html')


@app.route('/feedback/')
def feedback():

    sql = 'select ROWID,CategoryName from category'
    categories = query_sql(sql)
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
        sql = "insert into feedback (Subject, CategoryID, UserName, Email, Body, State, ReleaseTime) values (?,?,?,?,?,?,?)"
        execute_sql(sql,(subject,categoryid,username,email,body,state,releasetime))
        return redirect(url_for('feedback'))

@app.route('/admin/list/')
def feedback_list():
    key = request.args.get('key','')
    sql = 'select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c on c.ROWID = f.CategoryID WHERE f.Subject LIKE ? ORDER BY f.ROWID DESC '
    feedbacks = query_sql(sql,('%{}%'.format(key),))
    return render_template('feedback-list.html',items=feedbacks)

@app.route('/admin/edit/<id>/')
def edit_feedback(id=None):
    sql = 'select ROWID,CategoryName from category'
    categories = query_sql(sql)

    #获取当前ID的信息并绑定至form表单，以备修改
    sql = 'select rowid,* from feedback WHERE rowid = ?'
    current_feedback = query_sql(sql,(id,), one=True)
    return render_template('edit.html', categories=categories,item=current_feedback)

@app.route('/admin/save_edit/',methods=['POST'])
def save_feedback():
    if request.method == 'POST':
        #获取表单
        rowid = request.form.get('rowid',None)
        reply = request.form.get('reply')
        is_processed = 1 if request.form.get('is_processed',0) == 'on' else 0
        sql = 'update feedback set Reply = ?,State = ? WHERE rowid = ?'
        execute_sql(sql,(reply,is_processed,rowid))
        return redirect(url_for('feedback_list'))
        #return str(is_processed)
@app.route('/admin/feedback/del/<id>/')
def delete_feedback(id=0):
    sql = "delete from feedback WHERE ROWID = ?"
    execute_sql(sql,(id,))
    return redirect(url_for('feedback_list'))

if __name__ == '__main__':
    app.run()
