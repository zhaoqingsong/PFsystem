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
def execute_sql(sql,prm=()):
    c = get_db().cursor()
    c.execute(sql,prms)
    c.connection.commit()

# 执行用于选择数据的SQL语句
def query_sql(sql, prms=()):
    pass


#关闭连接（在当前app 上下文销毁时关闭连接）
@app.teardown_appcontext
def close_connection(exeption):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def pfs():
    return render_template('base.html')

@app.route('/feedback/')
def feedback():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = 'select ROWID,CategoryName from category'
    categories = c.execute(sql).fetchall()
    c.close()
    conn.close()
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
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        sql = "insert into feedback (Subject, CategoryID, UserName, Email, Body, State, ReleaseTime) values (?,?,?,?,?,?,?)"
        c.execute(sql,(subject,categoryid,username,email,body,state,releasetime))
        conn.commit()
        conn.close()
        return redirect(url_for('feedback'))

@app.route('/admin/list/')
def feedback_list():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = 'select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c on c.ROWID = f.CategoryID ORDER BY f.ROWID DESC '
    feedbacks = c.execute(sql).fetchall()
    conn.close()
    return render_template('feedback-list.html',items=feedbacks)

@app.route('/admin/edit/<id>/')
def edit_feedback(id=None):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = 'select ROWID,CategoryName from category'
    categories = c.execute(sql).fetchall()

    #获取当前ID的信息并绑定至form表单，以备修改
    sql = 'select rowid,* from feedback WHERE rowid = ?'
    current_feedback = c.execute(sql,(id,)).fetchone()
    c.close()
    conn.close()
    return render_template('edit.html', categories=categories,item=current_feedback)

@app.route('/admin/save_edit/',methods=['POST'])
def save_feedback():
    if request.method == 'POST':
        #获取表单
        rowid = request.form.get('rowid',None)
        reply = request.form.get('reply')
        is_processed = 1 if request.form.get('state',0) == 'on' else 0
        sql = 'update feedback set Reply = ?,State = ? WHERE rowid = ?'
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute(sql,(reply,is_processed,rowid))
        conn.commit()
        conn.close()
        return redirect(url_for('feedback_list'))


@app.route('/admin/feedback/del/<id>/')
def delete_feedback(id=0):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = "delete from feedback WHERE ROWID = ?"
    c.execute(sql,(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('feedback_list'))

if __name__ == '__main__':
    app.run()
