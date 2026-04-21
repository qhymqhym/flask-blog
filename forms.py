#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表单定义模块
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User


class LoginForm(FlaskForm):
    """
    登录表单
    """
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    """
    注册表单
    """
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        """
        验证用户名是否已存在
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')


class UpdateProfileForm(FlaskForm):
    """
    更新用户资料表单
    """
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('更新资料')

    def validate_username(self, username):
        """
        验证用户名是否已存在
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')


class ArticleForm(FlaskForm):
    """
    文章表单
    """
    title = StringField('标题', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('内容', validators=[DataRequired()])
    category_id = SelectField('分类', validators=[DataRequired()], coerce=int)
    tags = SelectMultipleField('标签', coerce=int)
    cover = FileField('封面图')
    status = SelectField('状态', choices=[('draft', '草稿'), ('published', '已发布')], validators=[DataRequired()])
    is_top = BooleanField('置顶')
    submit = SubmitField('保存')


class CommentForm(FlaskForm):
    """
    评论表单
    """
    content = TextAreaField('评论内容', validators=[DataRequired()])
    submit = SubmitField('提交评论')


class CategoryForm(FlaskForm):
    """
    分类表单
    """
    name = StringField('分类名称', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('保存')


class TagForm(FlaskForm):
    """
    标签表单
    """
    name = StringField('标签名称', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('保存')
