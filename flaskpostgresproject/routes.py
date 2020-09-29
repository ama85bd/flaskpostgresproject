import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, session, request
from flaskpostgresproject import app, db, bcrypt, mail
from flaskpostgresproject.forms import RegistrationForm, LoginForm, RequestRegistrationForm, RequestRegistrationForm, \
    PostForm, UpdateAccountForm
from flaskpostgresproject.models import EmailFirst, User, Post
from flask_mail import Message
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc())
    return render_template('index.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


def send_request_register(email):
    token = email.get_register_token()
    msg = Message('Registration Request for Techreptile Together', sender='tech.reptile20@gmail.com',
                  recipients=[email.email])
    msg.body = f'''To complete your registration, visit the following link:
    {url_for('requestregistration', token=token, _external=True)}
    
    If you did not make this request then simply ignore this email.
    '''
    mail.send(msg)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        firstemail = EmailFirst(email=form.email.data)
        firstemail_found = EmailFirst.query.filter_by(email=form.email.data).first()
        if firstemail_found:
            db.session.delete(firstemail_found)
            db.session.commit()
        else:
            db.session.add(firstemail)
            db.session.commit()
        send_request_register(firstemail)
        flash(f'An email has been sent on {form.email.data} please check and '
              f'complete your registration.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/register/<token>', methods=['GET', 'POST'])
def requestregistration(token):
    firstemail = EmailFirst.verify_register_token(token)
    if firstemail is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('register'))
    form = RequestRegistrationForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname=form.fullname.data, username=form.username.data,
                    phone=form.phone.data, email=form.email.data,
                    highestdegree=form.highestdegree.data, picture=picture_file,
                    institute=form.institute.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can login now', 'success')
        return redirect(url_for('login'))
    return render_template('requestregistration.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.picture = picture_file
        current_user.fullname = form.fullname.data
        current_user.highestdegree = form.highestdegree.data
        current_user.institute = form.institute.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.fullname.data = current_user.fullname
        form.highestdegree.data = current_user.highestdegree
        form.institute.data = current_user.institute
    image_file = url_for('static', filename='profile_pics/' + current_user.picture)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
