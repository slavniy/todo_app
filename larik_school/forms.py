from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import validators
from larik_school.models import User


def secure_password(form, field):
    if len(field.data) < 6:
        raise validators.ValidationError('Длина пароля меньше 6 символов!')
    if not any([letter.isdigit() for letter in field.data]):
        raise validators.ValidationError('Пароль должен содержать цифры')
    if not any(letter.islower() for letter in field.data):
        raise validators.ValidationError('Пароль должен содержать буквы в нижнем регистре')
    if not any(letter.isupper() for letter in field.data):
        raise validators.ValidationError('Пароль должен содержать буквы в верхнем регистре')
    
def not_exist_email(form, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise validators.ValidationError('Пользователь с таким Email уже существует!')

class RegistationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), not_exist_email])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6), secure_password])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class LessonsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Create lesson')

class ProblemForm(FlaskForm):
    question = TextAreaField('Вопрос', validators=[DataRequired()])
    category = SelectField('Выбор категории')
    file = FileField('Добавить файл')
    answer = StringField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Добавить вопрос')

class CategoryForm(FlaskForm):
    title = StringField('Название категории', validators=[DataRequired(), Length(min=3, max=30)])
    submit = SubmitField('Добавить')