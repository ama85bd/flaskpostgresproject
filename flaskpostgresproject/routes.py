import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, session, request, abort
from flaskpostgresproject import app, db, bcrypt, mail
from flaskpostgresproject.forms import RegistrationForm, LoginForm, RequestRegistrationForm, RequestRegistrationForm, \
    PostForm, UpdateAccountForm, CommentForm, ReplyCommentForm
from flaskpostgresproject.models import EmailFirst, User, Post, Comment, ReplyComment
from flask_mail import Message
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.all()
    comments = Comment.query.all()
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
    output_size = (125, 125)
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


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    comments = db.session.query(Comment).filter(Comment.post_id == post.id).all()
    commentid = Comment.query.filter_by(post_id=post.id).all()
    #comment_id = Comment.query.filter(Comment.post_id).all()
    reply_comments = db.session.query(ReplyComment).filter(
        ReplyComment.post_id == post.id and ReplyComment.comment_id == commentid.id).all()
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments,
                           reply_comments=reply_comments)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!!', 'danger')
    return redirect(url_for('index'))


@app.route("/post/<int:post_id>/comment", methods=['GET', 'POST'])
@login_required
def comment_post(post_id):
    form = CommentForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        comment = Comment(comment=form.comment.data, postID=post, Comment_author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted', 'success')
        return redirect(url_for('post', post_id=post.id))


@app.route("/post/<int:post_id>/reply_comment/<int:comment_id>", methods=['GET', 'POST'])
@login_required
def reply_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    # form = CommentForm()
    # reply_form = ReplyCommentForm()
    comments = db.session.query(Comment).filter(Comment.post_id == post.id).all()
    commentid = Comment.query.get_or_404(comment_id)
    text = request.form.get("reply_comment")
    replycomment = ReplyComment(replycomment=text, replyComID=commentid, postcommentID=post,
                                Comment_reply_author=current_user)
    db.session.add(replycomment)
    db.session.commit()
    flash('Your reply has been posted', 'success')
    return redirect(url_for('post', post_id=post.id))
    # return render_template('post.html', title=post.title, post=post, form=form, comments=comments,
    #    reply_form=reply_form)
