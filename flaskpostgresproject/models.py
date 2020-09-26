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
 username = db.Column(db.String(20), unique=True, nullable=False)
 email = db.Column(db.String(120), unique=True, nullable=False)
 image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
 password = db.Column(db.String(60), nullable=False)
 mobile_no = db.Column(db.Integer(11), nullable=False)
