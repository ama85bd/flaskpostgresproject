from flask import render_template, flash, redirect, url_for, session, request
from flaskpostgresproject import app, db, bcrypt, mail
from flaskpostgresproject.forms import RegistrationForm, LoginForm, RequestRegistrationForm, RequestRegistrationForm, \
    PostForm
from flaskpostgresproject.models import EmailFirst, User, Post
from flask_mail import Message


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
    msg = Message('Registration Request for Techreptile Together', sender='tech.reptile20@gmail.com', recipients=[email.email])
    msg.body = f'''To complete your registration, visit the following link:
    {url_for('requestregistration', token=token, _external=True)}
    
    If you did not make this request then simply ignore this email.
    '''
    mail.send(msg)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        firstemail = EmailFirst(email=form.email.data)
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname=form.fullname.data, username=form.username.data,
                    phone=form.phone.data, email=form.email.data,
                    highestdegree=form.highestdegree.data,
                    institute=form.institute.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can login now')
        return redirect(url_for('login'))
    return render_template('requestregistration.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
