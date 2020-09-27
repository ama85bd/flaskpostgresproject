from datetime import datetime
from flaskpostgresproject import db, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class EmailFirst(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    picture = db.Column(db.String(20), nullable=False, default='default.jpg')
    highestdegree = db.Column(db.String(120), nullable=False)
    institute = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
