from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from app.Utils.password import Password


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

class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver = db.Column(db.String(30))
    host = db.Column(db.String(30))
    db_name = db.Column(db.String(30))
    login = db.Column(db.String(30))
    password = db.Column(db.String(30))
    remark = db.Column(db.String(100))

    def __repr__(self):
        return '<DB {}>'.format(self.remark)

    def set_password(self, password):
        self.password = Password.encode(password)

    def get_password(self):
        return Password.decode(self.password)
