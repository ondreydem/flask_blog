from app import db
from flask_login import UserMixin

ROLE_USER = 0
ROLE_ADMIN = 1

'''User from left side (column "user_id") is following user from the right side (column "followed_id")'''
followers = db.Table('followers',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


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
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.user_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def get_feed(self):
        followed_posts = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.user_id == self.id).order_by(Post.timestamp.desc())
        return followed_posts

    def get_followed(self):
        return User.query.join(followers, (followers.c.followed_id == self.id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comments', backref='post', lazy='dynamic', cascade='all, delete')


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
