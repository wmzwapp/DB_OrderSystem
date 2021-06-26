# coding:utf8
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, redirect, url_for, flash
from forms import *
import time

# 初始化应用程序
app = Flask(__name__)       # app是Flask的实例，它接收包或者模块的名字作为参数，但一般都是传递__name__
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:73369648@localhost:3306/catering?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)
from models import *

# 登录视图函数
@app.route('/welcome')
@app.route('/')
def index():
    signupform = RegistrationForm(request.form)
    loginform = LogInForm(request.form)
    return render_template('welcome_login.html', signupform=signupform, loginform=loginform)

# 会员注册视图函数
@app.route('/member_signup', methods=['POST', 'GET'])
def signup():
    signupform = RegistrationForm(request.form)
    if request.method == 'POST':
        if signupform.validate():
            if db.session.query(Member).filter_by(Mname=signupform.username.data).first():
                flash("用户名已存在！")
                return redirect((url_for('signup')))
            else:
                member = Member(Mno='00000000', Mname=signupform.username.data,\
                                password_hash=set_password(signupform.password.data), Mphone=signupform.phone.data)
                try:
                    db.session.add(member)
                    db.session.commit()
                    flash("注册成功!请重新登录")
                    return redirect(url_for('login'))
                except Exception as e:
                    db.session.rollback()
                    return '<p>%s' % e
        else:
            return render_template("welcome_signup.html", signupform=signupform)
    return render_template('welcome_signup.html',signupform = signupform)

# 会员登录视图函数
@app.route('/member_login', methods=['POST', 'GET'])
def login():
    loginform = LogInForm(request.form)
    if request.method == 'POST':
        if loginform.validate():
            tmp = db.session.query(Member).filter_by(Mname=loginform.username.data).first()
            if tmp == None:
                flash("用户不存在")
            elif check_password(loginform.password.data, tmp.password_hash) or\
                    loginform.password.data == tmp.password_hash:
                return redirect(url_for('consumer_login',type=tmp.Mno))
            else:
                flash("密码错误")
    return render_template("welcome_login.html", loginform=loginform)

# 确认就餐信息视图函数
@app.route('/consumer_login/<type>', methods=['POST', 'GET'])
def consumer_login(type):
    consumerform = ConsumerForm(request.form)
    if request.method == 'POST':
        if consumerform.validate():
            consumer_num = int(consumerform.consumer_num.data)
            if consumer_num == 0:
                flash("请输入正确的就餐人数")
            elif consumer_num > 15:
                flash("抱歉，本餐厅最多支持15人同时就餐")
            else:
                num = db.session.query(Bill).count()
                if type == 'not_member':
                    return redirect(url_for('order_dishes', consumer='not_member', listid=num, consumer_num=consumer_num))
                else:
                    return redirect(url_for('order_dishes', consumer=type, listid=num, consumer_num=consumer_num))
    return render_template('consumer_login1.html', form=consumerform)

allfood = []        # 记录所有菜品
alllist = []        # 记录本次订单的信息
allpay = 0         # 记录总金额
allchose = 0         # 记录点菜数量

# 点餐视图函数
@app.route("/order_dishes/<consumer>/<listid>/<consumer_num>", methods=['POST','GET'])
def order_dishes(consumer, listid, consumer_num):
    # 获取菜单内容
    global allfood
    global alllist
    global allpay
    global allchose
    url_args = [consumer, listid, consumer_num]
    if len(allfood) == 0:
        allfood = db.session.query(Menu).all()
    if request.method == 'GET':
        # 给表单赋初值
        alllist.clear()
        allpay = 0
        allchose = 0
        for food in allfood:
            list = ListForm(request.form, lFno=food.mFno)
            alllist.append(list)
        return render_template('order_dishes1.html', foods=allfood, lists=alllist, foodnum=len(alllist), \
                               allcost=allpay, allchose=allchose, url_args=url_args)
    elif request.method == 'POST':
        # 将 request.form 反转
        postform = {v : k for k, v in request.form.items()}
        # 增加或删除点的菜
        if '添加' in postform.keys():
            target = postform['添加']
            targetlist,num,cost = target.split('add',2)
            alllist[int(targetlist)].Lnum = int(num)+1
            allchose += 1
            allpay += float(cost)
        else:
            target = postform['删除']
            targetlist,num,cost = target.split('del',2)
            if (alllist[int(targetlist)].Lnum > 0):
                allchose -= 1
                allpay -= float(cost)
            if(int(num)>0):
                alllist[int(targetlist)].Lnum = int(num) - 1
        return render_template('order_dishes1.html', foods=allfood, lists=alllist, foodnum=len(alllist), \
                               allcost=allpay, allchose=allchose, url_args=url_args)

# 确认订单
@app.route("/submit/<consumer>/<listid>/<consumer_num>", methods=['POST'])
def submit(consumer, listid, consumer_num):
    global alllist
    global allpay
    if len(alllist) == 0:
        return redirect(url_for('order_dishes', consumer=consumer, listid=listid, consumer_num=consumer_num))
    # 将alllist中的内容存入数据库list表中，同时生成相应的bill记录
    if request.method == 'POST':
        allinsert = []              # 要插入数据库的记录 List
        mylist = []                 # 所有点的菜       ListForm
        # list
        for list in alllist:
            if list.Lnum > 0:
                insertlist = List(Lno='L'+listid.zfill(7), lFno=list.lFno.data, Lnum=list.Lnum)
                allinsert.append(insertlist)
                mylist.append(list)
        # bill
        if consumer == 'not_member':
            bill = Bill(Bno='00000000', Bcost=allpay, Btime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) \
                        , bCno='00000000', bLno='L'+listid.zfill(7), Bnum=consumer_num)
        else:
            bill = Bill(Bno='00000000', Bcost=allpay, Btime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) \
                        , bCno=consumer, bLno='L' + listid.zfill(7), Bnum=consumer_num)
        allinsert.append(bill)
        try:
            db.session.add_all(allinsert)
            db.session.commit()
        except Exception as e:
            return '%s' % e
        return redirect(url_for('display_list',consumer=consumer, listid=listid, consumer_num=consumer_num))


# 展示订单界面
@app.route("/display_list/<consumer>/<listid>/<consumer_num>", methods=['POST', 'GET'])
def display_list(consumer, listid, consumer_num):
    url_args = [consumer, listid, consumer_num]
    foodnum = []
    foods = []
    length = 0
    pay = 0
    if consumer != 'not_member':
        member = db.session.query(Member).get(consumer)
        name = member.Mname
    else:
        name = 'not_member'
    if request.method == 'GET':
        mylists = db.session.query(List).filter_by(Lno='L'+listid.zfill(7)).all()
        length = len(mylists)
        for mylist in mylists:
            foodnum.append(mylist.Lnum)
            foods.append(db.session.query(Menu).filter_by(mFno=mylist.lFno).one())
            pay += foods[-1].Fprice
        return render_template('display_list1.html', name=name, foodnum=foodnum, foods=foods, url_args=url_args,\
                               length=length, pay=pay)

# 会员信息界面
@app.route("/member_info/<consumer>/<listid>/<consumer_num>", methods=['POST', 'GET'])
def member_info(consumer, listid, consumer_num):
    url_args=[consumer, listid, consumer_num]
    # 获取用户基本信息
    member = db.session.query(Member).get(consumer)
    if request.method == 'GET':
        # 获取用户消费记录
        mybills = db.session.query(Bill).filter_by(bCno=consumer).all()
        billnum = len(mybills)
        mylists = []
        if billnum > 0:
            for mybill in mybills:
                mylist = []
                lists = db.session.query(List).filter_by(Lno=mybill.bLno).all()
                for list in lists:
                    mylist.append(db.session.query(Food.Fname).filter_by(Fno=list.lFno).scalar()\
                                  + '*'+str(list.Lnum))
                mylists.append(mylist)
        return render_template('member_info1.html', member=member, mylists=mylists, bills=mybills, billnum=billnum, url_args=url_args)
    elif request.method == 'POST':
        return redirect(url_for('change_password', type='M', id=member.Mno))

# 员工登录界面
@app.route("/staff_login", methods=['POST', 'GET'])
def staff_login():
    staffform = LogInForm(request.form)
    if request.method == 'POST':
        tmp = db.session.query(Staff).filter_by(sSname=staffform.username.data).first()
        if tmp:
            if staffform.password.data == tmp.password_hash or check_password(staffform.password.data, tmp.password_hash):
                return redirect(url_for('staff_info', staff_id=tmp.sSno))
            else:
                flash('密码错误')
        else:
            flash('用户不存在')
        return redirect(url_for('staff_login'))
    return render_template('notmember_login1.html', form=staffform)

# 管理员登录界面
@app.route("/admin_login", methods=['POST', 'GET'])
def admin_login():
    adminform = LogInForm(request.form)
    if request.method == 'POST':
        tmp = db.session.query(Admin).filter_by(Aname=adminform.username.data).first()
        if tmp:
            if adminform.password.data == tmp.password_hash or\
                    check_password(adminform.password.data, tmp.password_hash):
                return redirect(url_for('admin_only', id=tmp.Ano))
            else:
                flash('密码错误')
        else:
            flash('用户不存在')
        return redirect(url_for('admin_login'))
    return render_template('notmember_login1.html', form=adminform)

# 员工信息界面
@app.route("/staff_info/<staff_id>", methods=['POST', 'GET'])
def staff_info(staff_id):
    staffinfo = db.session.query(StaffInfo).get(staff_id)
    if request.method == 'POST':
        return redirect(url_for('change_password', type='S', id=staff_id))
    return render_template('staff_info1.html', staffinfo=staffinfo)

# 管理者信息界面
@app.route("/admin_only/<id>", methods=['POST', 'GET'])
def admin_only(id):
    admin = db.session.query(Admin).get(id)
    if request.method == 'GET':
        # 收集账单信息及收支情况
        allbill = db.session.query(Bill).all()
        # 计算支出情况
        allcost = 0
        lists = db.session.query(List).all()
        for list in lists:
            allcost += db.session.query(Food.Fcost).filter_by(Fno=list.lFno).scalar() * list.Lnum
        # 计算收入情况
        income = 0
        for bill in allbill:
            income += bill.Bcost
        # 查询员工信息
        mystaff = db.session.query(StaffInfo).all()
        # 查询菜式信息
        foods = db.session.query(Food).all()
        # 渲染
        return render_template('admin_only1.html', name=admin.Aname, allbill=allbill, allcost=allcost, income=income,\
                               mystaff=mystaff, foods=foods)
    elif request.method == 'POST':
        return redirect(url_for('change_password', type='A', id=admin.Ano))



# 修改密码界面
@app.route("/change_password/<type>/<id>", methods=['POST', 'GET'])
def change_password(type, id):
    alterform = AlterForm(request.form)
    if request.method == 'POST':
        if(alterform.validate()):
            if type == 'S':
                user = db.session.query(Staff).get(id)
            elif type == 'A':
                user = db.session.query(Admin).get(id)
            elif type == 'M':
                user = db.session.query(Member).get(id)
            if user.password_hash == alterform.old_password.data or\
                    check_password(alterform.old_password.data, user.password_hash):
                user.password_hash = set_password(alterform.new_password.data)
                try:
                    db.session.merge(user)
                    db.session.commit()
                    flash('修改密码成功，请重新登录')
                    return redirect(url_for('index'))
                except Exception as e:
                    db.rollback()
                    return '%s' % e
            else:
                flash('请输入正确的旧密码')
                return redirect(url_for('change_password', type=type, id=id))
        else:
            return render_template('change_password1.html', form=alterform)
    return render_template('change_password1.html', form=alterform)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug='True')
