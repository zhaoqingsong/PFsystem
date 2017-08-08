import hashlib
from flask import render_template,request,session,redirect,url_for
from flask.views import View,MethodView
from sqlmap.sqljob import connect_db,execute_db,query_db
#基于类的视图

class Reguser(View):
    methods = ['POST','GET']
    def dispatch_request(self):
        return render_template('reg.html')

class UserLogin(View):
    methods = ['GET','POST']
    def dispatch_request(self):
        if request.method == 'POST':
            username = request.form.get('username')
            pass_salt = "124%wer0514"
            pwd = request.form.get('pwd')
            md5 = hashlib.md5()
            md5.update("{}{}{}".format(pwd, username, pass_salt).encode('utf-8'))
            md5_pass = md5.hexdigest()
            # return "{}{}".format(pwd,username).encode('utf-8')
            # return md5_pass
            sql = 'select count(*) as [Count] from UserInfo where UserName = ? and Password = ?;'
            result = query_db.query_sql(sql, (username, md5_pass), one=True)

            if int(result.get('Count')) > 0:
                session['adminuser'] = username
                return redirect(url_for('feedback_list'))
            flash('用户名或者密码不匹配,请重新输入!')

        return render_template('login.html')

#基于方法的视图
class MyRegUser(MethodView):
    def get(self):
        return render_template('reg.html')

    def post(self):
        render_template('reg.html')
