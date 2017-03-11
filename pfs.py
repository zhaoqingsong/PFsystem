import sqlite3
from flask import Flask,render_template,redirect,url_for,request
from datetime import datetime

DATABASE_URL = r'.\db\feedback.db'
app = Flask(__name__)
app.debug = True

conn = sqlite3.connect(DATABASE_URL,check_same_thread=False)
c = conn.cursor()

@app.route('/')
def pfs():
    return render_template('base.html')
@app.route('/feedback/')
def feedback():
    # categories = [(1,'产品质量'),(2,'客户服务'),(3,'购买支付')]
    sql = 'select * from category'
    categories = c.execute(sql).fetchall()
    # c.close()
    # conn.close()
    return render_template('post.html',categories = categories)

@app.route('/post_feedback/',methods=['POST'])
def post_feedback():
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
    sql = 'select ROWID,* FROM feedback ORDER BY ROWID DESC '
    feedbacks = c.execute(sql).fetchall()
    conn.close()
    return render_template('feedback-list.html',items = feedbacks)

if __name__ == '__main__':
    app.run()
