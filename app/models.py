from app import db
from flask_login import UserMixin

ROLE_USER = 0
ROLE_ADMIN = 1


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.Text(20))
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    about = db.Column(db.Text(200))
    date_of_birth = db.Column(db.Date)
    last_seen = db.Column(db.DateTime)
    avatar = db.Column(db.LargeBinary, default=None)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comments', backref='author', lazy='dynamic')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comments', backref='post', lazy='dynamic')


    def get_feed(self):
        pass


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



