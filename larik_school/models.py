from larik_school import db
from datetime import datetime


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"Task {self.id}: {self.content}"
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    lessons = db.relationship('Lesson', backref='author', lazy=True)

    def __repr__(self):
        return f'Пользователь {self.username}'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    color = db.Column(db.String)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns} 
    

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)