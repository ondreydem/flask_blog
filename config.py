import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


WTF_CSRF_ENABLED = True
SECRET_KEY = '637dd3e8e2c1c82150eeaa2ffd5604ae9786c3a702ea47382966a544681e5a91'

