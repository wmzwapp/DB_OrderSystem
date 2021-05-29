# coding=utf8
from test import db
from werkzeug.security import generate_password_hash, check_password_hash


class Member(db.Model):
    __tablename__ = 'member'
    Mno = db.Column(db.String(8), primary_key=True)
    mMlevel = db.Column(db.Enum('d', 'c', 'b', 'a', 's'), server_default='d')
    Mdiscount = db.Column(db.DECIMAL(4, 2))
    Mphone = db.Column(db.String(11))
    Mname = db.Column(db.String(10))
    password_hash = db.Column(db.String(200))

class Admin(db.Model):
    __tablename__ = 'admin'
    Ano = db.Column(db.String(8), primary_key=True)
    Aname = db.Column(db.String(10))
    password_hash = db.Column(db.String(200))

class Staff(db.Model):
    __tablename__ = 'staff_login'
    sSno = db.Column(db.String(8), primary_key=True)
    sSname = db.Column(db.String(10))
    password_hash = db.Column(db.String(200))

class Consumer(db.Model):
    __tablename__ = 'consumer'
    Cno = db.Column(db.String(8), primary_key=True)
    Cnum = db.Column(db.Integer)

class Menu(db.Model):
    __tablename__ = 'menu'
    mFno = db.Column(db.String(8), primary_key=True)
    Fname = db.Column(db.String(20))
    Fprice = db.Column(db.DECIMAL(10, 2))
    mFtype = db.Column(db.Enum('川菜', '湘菜', '粤菜', '鲁菜', '日料', '甜品', '饮品'))

class Food(db.Model):
    __tablename__ = 'food'
    Fno = db.Column(db.String(8), primary_key=True)
    Fname = db.Column(db.String(20))
    Fcost = db.Column(db.DECIMAL(10, 2))
    Fdetail = db.Column(db.String(100))
    fSno = db.Column(db.String(8))
    Ftype = db.Column(db.Enum('川菜', '湘菜', '粤菜', '鲁菜', '日料', '甜品', '饮品'))

class List(db.Model):
    __tablename__ = 'list'
    Lno = db.Column(db.String(8))
    lFno = db.Column(db.String(8))
    Lnum = db.Column(db.Integer)
    Lpk = db.Column(db.Integer, primary_key=True)

class Bill(db.Model):
    __tablename__ = 'bill'
    Bno = db.Column(db.String(8), primary_key=True)
    Bcost = db.Column(db.DECIMAL(10, 2))
    Btime = db.Column(db.DateTime)
    bCno = db.Column(db.String(8))
    bLno = db.Column(db.String(8))
    Bnum = db.Column(db.Integer)

class StaffInfo(db.Model):
    __tablename__ = 'staff'
    Sno = db.Column(db.String(8), primary_key=True)
    Sname = db.Column(db.String(10))
    Saddr = db.Column(db.String(45))
    Sintime = db.Column(db.Date)
    Sphone = db.Column(db.String(11))
    Spay = db.Column(db.DECIMAL(8, 2))
    Stype = db.Column(db.Enum('server', 'chef'))
    Sex = db.Column(db.Enum('F', 'M'))

def set_password(password):
    return generate_password_hash(password)

def check_password(password, password_hash):
    return check_password_hash(password_hash, password)


# 生成模板类
db.create_all()
