import datetime
import sqlite3

from flask import render_template, flash, redirect, url_for, g, request, session
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db, lm
from .forms import LoginForm, RegisterForm, PostForm, EditProfileForm, CommentForm
from .models import User, Post, Comments
from werkzeug.security import generate_password_hash, check_password_hash
from config import POST_PER_PAGE


def get_user_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    date_of_birth = user.date_of_birth.strftime("%d %B %Y")
    if user.last_seen:
        last_seen = user.last_seen.strftime("%H:%M %d.%m.%Y")
    else:
        last_seen = 'Never'
    user_info = {'email': user.email,
                 'date_of_birth': date_of_birth,
                 'about': user.about,
                 'last_seen': last_seen,
                 'user_id': user.id,
                 'avatar': user.avatar,
                 'username': user.nickname}
    return user_info


def get_current_url(page_route):
    session['current_page'] = page_route
    print(session.get('current_page'))
    return session['current_page']


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@app.route('/index/<int:page>', methods=['POST', 'GET'])
def index(page=1):
    get_current_url(request.url)
    if g.user.is_authenticated:
        posts = g.user.get_feed().paginate(page, POST_PER_PAGE, False)
        comment = CommentForm()
        form = PostForm()
        return render_template('index.html',
                               user=g.user,
                               posts=posts,
                               comment=comment,
                               form=form)
    else:
        return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.datetime.now()
        db.session.commit()


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    next = request.args.get('next')
    if g.user is not None and g.user.is_authenticated:
        return redirect(next or url_for('profile', user_id=g.user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(next or url_for('profile', user_id=user.id))
        else:
            flash('Wrong password or user does not exist')
    return render_template('login.html',
                           form=form,
                           p_title='Log In')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            checked_email = db.session.query(User).filter_by(email=form.email.data).first()
            if checked_email is not None:
                flash('User with this email is already exist')
                return redirect(url_for('register'))
            else:
                hashed_psw = generate_password_hash(form.password.data)
                user = User(nickname=form.name.data,
                            email=form.email.data,
                            password=hashed_psw,
                            date_of_birth=form.date_of_birth.data)
                db.session.add(user)
                db.session.commit()
                db.session.add(user.follow(user))
                db.session.commit()
                return redirect(request.args.get('next') or url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(e, 'danger')
    return render_template('register.html',
                           p_title='Register',
                           form=form)


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@app.route('/profile/<int:user_id>/<int:page>', methods=['GET', 'POST'])
@login_required
def profile(user_id, page=1):
    get_current_url(request.url)
    user = User.query.filter_by(id=user_id).first()
    subscribers = user.followers.count() - 1
    posts = user.posts.paginate(page, POST_PER_PAGE, False)
    username = user.nickname
    comment = CommentForm()
    form = PostForm()
    return render_template('profile.html',
                           p_title=f'{username}\'s profile',
                           username=username,
                           posts=posts,
                           info=get_user_info(user_id),
                           comment=comment,
                           form=form,
                           subscribers=subscribers,
                           user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You're logout")
    return redirect(url_for('login'))


@app.route('/add_post', methods=['POST', 'GET'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(title=form.title.data,
                        body=form.body.data,
                        timestamp=datetime.datetime.now(),
                        user_id=g.user.id)
            db.session.add(post)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(e, 'danger')
    return redirect(session.get('current_page'))


@app.route('/delete/post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if g.user.is_authenticated and post.author.id == g.user.id:
        try:
            db.session.delete(post)
            db.session.commit()
            return redirect(session.get('current_page'))
        except Exception as e:
            db.session.rollback()
            flash(e, 'danger')


@app.route('/profile/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        try:
            user = User.query.get(g.user.id)
            if form.about.data:
                user.about = form.about.data
            if request.files['file']:
                file = request.files['file']
                img = file.read()
                avatar = sqlite3.Binary(img)
                user.avatar = avatar
            db.session.add(g.user)
            db.session.commit()
            return redirect(url_for('profile', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash(e, 'danger')
    return render_template('edit_profile.html', form=form)


@app.route('/profile/<int:user_id>/followers')
@login_required
def followers(user_id):
    user = User.query.filter_by(id=user_id).first()
    username = user.nickname
    followers = user.get_followed()
    return render_template('followers.html',
                           username=username,
                           user_id=user.id,
                           followers=followers,
                           info=get_user_info(user_id))


@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST' and current_user.is_following(user) == False:
        try:
            subscribe = current_user.follow(user)
            db.session.add(subscribe)
            db.session.commit()
            return redirect(url_for('profile', user_id=user.id))
        except Exception as e:
            flash(e, 'danger')
    flash('something go wrong')
    return redirect(url_for('profile', user_id=user.id))


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST' and current_user.is_following(user) == True:
        try:
            unsubscribe = current_user.unfollow(user)
            db.session.add(unsubscribe)
            db.session.commit()
            return redirect(url_for('profile', user_id=user.id))
        except Exception as e:
            flash(e, 'danger')
    flash('something go wrong')
    return redirect(url_for('profile', user_id=user.id))


@login_required
@app.route('/render_avatar/<user_id>')
def render_avatar(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.avatar


@login_required
@app.route('/add_comment', methods=['POST'])
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        try:
            post_id = request.form['post_id']
            post = Post.query.get(post_id)
            author_id = post.author.id
            comment = Comments(body=form.body.data,
                               timestamp=datetime.datetime.now(),
                               post_id=post_id,
                               user_id=g.user.id)
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(e, 'danger')
    return redirect(session.get('current_page'))


@app.route('/delete/comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comments.query.filter_by(id=comment_id).first()
    if g.user.is_authenticated and comment.author.id == g.user.id:
        try:
            db.session.delete(comment)
            db.session.commit()
            return redirect(session.get('current_page'))
        except Exception as e:
            db.session.rollback()
            flash(e, 'danger')


# so, is it need..?
@app.route('/post/<int:post_id>')
def post_page(post_id):
    pass
