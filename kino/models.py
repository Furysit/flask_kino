from kino import db, manager
from flask_login import UserMixin

@manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)


class Title(db.Model):
    __tablename__ = 'title'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    movie = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(250), nullable=False)
    img_path = db.Column(db.String(250))

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(50), nullable = False)
    password = db.Column(db.String(250), nullable = False)
    
