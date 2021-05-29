# coding=utf8
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField, IntegerField

class RegistrationForm(Form):
    username = TextField(
        label='用户名',
        validators=[
            validators.data_required('用户名不能为空!'),
            validators.Length(min=3, max=20, message='用户名长度不合法（3-20字符）')],
        render_kw={'placeholder': '用户名'}
    )
    phone = TextField(
        label='手机号',
        validators=[
            validators.data_required('手机号不能为空!'),
            validators.Length(min=11, max=11, message='请输入正确的手机号（11位）')],
        render_kw={'placeholder': '手机号'}
    )
    password = PasswordField(
        label='密码',
        validators=[
            validators.data_required('密码不能为空!'),
            validators.Length(min=5, max=30, message='密码长度不合法（5-30字节）'),
            validators.equal_to('password_cfm', message='两次输入的密码必须匹配！')],
        render_kw={'placeholder': '密码'}
    )
    password_cfm = PasswordField(
        label='确认密码',
        validators=[
            validators.required('请再次输入密码'),
            validators.Length(min=5, max=30, message='密码长度不合法（5-30字节）')],
        render_kw={'placeholder': '确认密码'}
    )


class LogInForm(Form):
    username = TextField(
        label='用户名',
        validators=[
                validators.data_required('用户名不能为空!'),
                validators.Length(min=2, max=10, message='用户名长度不合法（2-10字节）')],
        render_kw={'placeholder': '用户名'}
    )
    password = PasswordField(
        label='密码',
        validators=[
            validators.data_required('密码不能为空!'),
            validators.Length(min=5, max=30, message='密码长度不合法（5-30字节）')],
        render_kw={'placeholder': '密码'}
    )

class ConsumerForm(Form):
    consumer_num = TextField(
        label='就餐人数',
        validators=[
            validators.data_required('请输入就餐人数!'),
            validators.regexp(r'\d+', message='请输入数字')]
    )

class ListForm(Form):
    choose = BooleanField(label='选择', render_kw={'type': 'hidden'})
    lFno = StringField(label='菜式编号', render_kw={'type': 'hidden'})
    Lnum = 0

class MenuForm(Form):
    choose = BooleanField(label='选择')
    mFno = StringField(label='菜式编号')
    Fname = StringField(label='菜式名称')
    Fprice = StringField(label='价格')
    mFtype = StringField(label='类型')
    Fnum = IntegerField(label='菜式数量')

class AlterForm(Form):
    old_password = PasswordField(
        label='旧密码',
        validators=[
            validators.data_required('密码不能为空!'),
            validators.Length(min=5, max=30, message='密码长度不合法（5-30字节）')],
        render_kw={'placeholder': '旧密码'}
    )
    new_password = PasswordField(
        label='新密码',
        validators=[
            validators.data_required('密码不能为空!'),
            validators.Length(min=5, max=30, message='密码长度不合法（5-30字节）'),
            validators.equal_to('new_password_cfm', message='两次输入的密码必须匹配！')],
        render_kw={'placeholder': '新密码'}
    )
    new_password_cfm = PasswordField(
        label='确认密码',
        validators=[
            validators.data_required('密码不能为空!'),
            validators.Length(min=5, max=30, message='密码长度不合法（5-30字节）')],
        render_kw={'placeholder': '确认密码'}
    )
