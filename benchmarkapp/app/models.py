from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    who_we_are = db.Column(db.String(256))
    what_we_do = db.Column(db.String(256))
    best_submitted_file = db.Column(db.Integer, db.ForeignKey('submitted_file.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SubmittedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(140), unique=True)
    reference_file = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tab_absc = db.Column(db.String(4096))
    tab_hausdorff = db.Column(db.String(4096))
    tab_middle_completeness = db.Column(db.String(4096))
    tab_middle_accurracy = db.Column(db.String(4096))
    real_size = db.Column(db.Integer)
    estimated_size = db.Column(db.Integer)

    def __repr__(self):
        return '<SubmittedFile {} {}>'.format(self.id, self.filename)


def del_sub_file(sub_file):
    db.session.delete(sub_file)
    db.session.commit()
    user = User.query.filter_by(id=sub_file.user_id).first()
    if user.best_submitted_file == sub_file.id:
        user.best_submitted_file = None
        db.session.commit()
    return True


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
