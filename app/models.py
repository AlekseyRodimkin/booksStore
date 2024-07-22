from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app import db, manager
from app import admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose


class Exit(BaseView):
    """Вкладка админ панели"""

    @expose('/')
    def exit_page(self):
        return self.render('admin/exit_page/index.html')


class User(db.Model, UserMixin):
    """Модель пользователя"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    orders = relationship("Order")  # один ко многим к Order

    def __repr__(self):
        return self.login


class Order(db.Model):
    """Модель заказа"""
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10))
    start_rent = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))  # многие к одному к User
    book = relationship("Book", uselist=False)  # один к одному к Book


class Book(db.Model):
    """Модель книги"""
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50))
    year = db.Column(db.Integer)
    image_link = db.Column(db.String(200))
    filename = db.Column(db.String(30))
    order = db.Column(db.Integer, ForeignKey('orders.id'))  # один к одному к Order

    def __repr__(self):
        return self.name


# Adding in admin panel
admin.add_view(ModelView(User, db.session, name='Пользователи'))
admin.add_view(ModelView(Book, db.session, name='Книги'))
admin.add_view(ModelView(Order, db.session, name='Заказы'))
admin.add_view(Exit(name='Выход', endpoint='exit'))


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
