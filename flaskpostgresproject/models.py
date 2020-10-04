from datetime import datetime
from flaskpostgresproject import db, app, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class EmailFirst(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)

    def get_register_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_email': self.id}).decode('utf-8')

    @staticmethod
    def verify_register_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_email = s.loads(token)['user_email']
        except:
            return None
        return EmailFirst.query.get(user_email)

    def __repr__(self):
        return f"Email('{self.email}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    picture = db.Column(db.String(20), nullable=False, default='default.jpg')
    highestdegree = db.Column(db.String(120), nullable=False)
    institute = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='Comment_author', lazy=True)
    comments_author_reply = db.relationship('ReplyComment', backref='Comment_reply_author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.picture}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='postID', lazy=True)
    postcomments = db.relationship('ReplyComment', backref='postcommentID', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_comment = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    replycomments = db.relationship('ReplyComment', backref='replyComID', lazy=True)


    def __repr__(self):
        return f"Post('{self.comment}', '{self.date_comment}')"


class ReplyComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_comment = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    replycomment = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.comment}', '{self.date_comment}')"