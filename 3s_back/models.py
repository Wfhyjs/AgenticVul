from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from nltk import app

db = SQLAlchemy()


# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Uname = db.Column(db.String(100), unique=True, nullable=False)
    Uemail = db.Column(db.String(100), unique=True, nullable=False)
    Upassword = db.Column(db.String(100), nullable=False)
    UFacePath = db.Column(db.String(255), default='photo/default.png')
    Uorganization = db.Column(db.String(100), default='Uknown')
    Uphone = db.Column(db.String(11), default='Uknown')
    Uposition = db.Column(db.String(100), default='Uknown')
    UFirstName = db.Column(db.String(100), default='Uknown')
    ULastName = db.Column(db.String(100), default='Uknown')

    def __repr__(self):
        return f'<User {self.Uname}>'


class ProjectDetection(db.Model):
    __tablename__ = 'project_detection'
    PID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    Pname = db.Column(db.String(100), unique=True, nullable=False)
    Ptime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    Pfile = db.Column(db.Integer, default=-1, nullable=False)
    Pfunction = db.Column(db.Integer, default=-1, nullable=False)
    Pvul = db.Column(db.Integer, default=-1, nullable=False)
    Pfix = db.Column(db.Integer, default=0, nullable=False)
    Pdanger = db.Column(db.Float, default=-1, nullable=False)
    Pstatus = db.Column(db.String(100), default='未检测', nullable=False)
    Pfilepath = db.Column(db.String(255), nullable=False)
    Pmodel = db.Column(db.String(255), default='ReGVD', nullable=False)
    Pfuncpath = db.Column(db.String(255), default='', nullable=False)

    user = db.relationship('User', backref=db.backref('projects', lazy=True))