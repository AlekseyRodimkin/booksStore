from datetime import datetime
from flask_login import UserMixin
from app import db, manager
from app import admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose


class Exit(BaseView):
    """Вкладка админ панели"""

    @expose('/')
    def exit_page(self):
        return self.render('admin/exit_page/index.html')


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50))
    year = db.Column(db.Integer)
    link = db.Column(db.String(200))

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    box = db.relationship('Box', backref='user', uselist=False)  # один к одному с коробкой

    def __repr__(self):
        return self.login


class Box(db.Model):
    __tablename__ = 'user_have'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'))
    have = db.Column(db.Boolean, default=False)
    start_rent = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))  # Foreign key

    def __repr__(self):
        return


# Adding in admin panel
admin.add_view(ModelView(User, db.session, name='Пользователи'))
admin.add_view(ModelView(Book, db.session, name='Книги'))
admin.add_view(Exit(name='Выход', endpoint='exit'))


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
