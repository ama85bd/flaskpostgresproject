from flaskpostgresproject import db


class EmailFirst(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"Email('{self.email}')"

# class User(db.Model):
#  id = db.Column(db.Integer, primary_key=True)
#  username = db.Column(db.String(20), unique=True, nullable=False)
#  email = db.Column(db.String(120), unique=True, nullable=False)
