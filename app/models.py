from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    department = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    last_login = db.Column(db.DateTime, default=datetime.now)


    def __repr__(self):
        return '<User {}>'.format(self.username+'|'+self.department)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Flask-Login keeps track of the logged in user by storing its unique identifier in Flask's user session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))