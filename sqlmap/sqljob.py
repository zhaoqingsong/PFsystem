import sqlite3
import os
from flask.views import View,MethodView
from flask import Flask,render_template,redirect,url_for,make_response
from flask import request,g,flash,send_from_directory,session
from datetime import datetime,timedelta

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

# 建立数据库连接
class connect_db():
    def get_db():
        db = getattr(g,'_database',None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE_URL)
            db.row_factory = make_dicts
        return db

# 执行SQL语句不返回数据结果
class execute_db():
    def execute_sql(sql,prms=()):
        c = connect_db.get_db().cursor()
        c.execute(sql, prms)
        c.connection.commit()

# 执行用于选择数据的SQL语句
class query_db():
    def query_sql(sql, prms=(), one=False):
        c = connect_db.get_db().cursor()
        result = c.execute(sql, prms).fetchall()
        c.close()
        return (result[0] if result else None) if one else result