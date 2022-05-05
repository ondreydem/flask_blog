from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileSize, FileAllowed
from wtforms import TextAreaField, PasswordField, SubmitField, StringField, EmailField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[Email(), DataRequired()])
    password = PasswordField('your password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    password = PasswordField('your password', validators=[DataRequired()])
    email = EmailField('email', validators=[Email(), DataRequired()])
    submit = SubmitField('Sign In')
    repeat_password = PasswordField('repeat password',
                                    validators=[DataRequired(),
                                    EqualTo('password', message='Password must match!')])
    date_of_birth = DateField('date_of_birth', validators=[DataRequired()])


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])


class EditProfileForm(FlaskForm):
    about = TextAreaField('about', validators=[Length(max=200)])
    avatar = FileField('avatar', validators=[FileAllowed(['png'], 'Must be a .png')])


class CommentForm(FlaskForm):
    body = StringField('comment', validators=[Length(max=200)])


