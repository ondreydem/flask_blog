from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import datetime
import os

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
# lm.session_protection = 'strong'
lm.login_view = 'login'

from app import views, models
from .models import User
from config import basedir

if 'app.db' not in os.listdir(basedir):
    db.create_all()
    data = datetime.datetime.now()
    try:
        user1 = User(nickname='Andrey',
                     email='andrey@gmail.com',
                     password='123',
                     date_of_birth=data)
        user2 = User(nickname='Sergey',
                     email='sergey@gmail.com',
                     password='123',
                     date_of_birth=data)
        user3 = User(nickname='Nastya',
                     email='nastya@gmail.com',
                     password='123',
                     date_of_birth=data)
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()
    except Exception as e:
        print(e, 'DANGER')
