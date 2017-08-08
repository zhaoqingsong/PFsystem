#-*- coding:utf-8 -*-
import hashlib
md5 = hashlib.md5()
md5.update('how to use md5 in python hashlib?'.encode('utf-8'))
def calc_md5(userpassword):
    md5 = hashlib.md5()
    md5.update(.encode('utf-8'))
