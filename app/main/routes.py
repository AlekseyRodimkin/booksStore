import flask_login
import os
import io
import datetime
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Book, Order
from app.main import bp

# for pay
from cloudipsp import Api, Checkout


@bp.before_request
def before_request():
    """The function of updating the last visit"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """The function of the main page"""
    books = Book.query.order_by(Book.price).all()
    return render_template('index.html', title='Главная', data=books)


@bp.route('/user/<username>')
@login_required
def user(username):
    """
    Profile function
    :param username: str
    :return: render profile and data
    """
    user = db.first_or_404(sa.select(User).where(User.username == username))
    orders = flask_login.current_user.orders
    time_now = datetime.datetime.now()
    return render_template('user.html', user=user, data=orders, now=time_now)


@bp.route('/buy/<int:id>')
def book_buy(id):
    """
    Функция покупки. Необходим VPN.

    merchant_id: from account in Fondy
    :param id: id книги
    :return: url transaction
    """
    book = Book.query.get(id)  # get book.id from database

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(book.price) + '00'
    }
    url = checkout.url(data).get('checkout_url')

    user_id = flask_login.current_user.id
    book_id = id
    status = 'buy'
    new_order = Order(status=status, user_id=user_id, book=book)
    db.session.add(new_order)
    db.session.commit()
    return redirect(url)


@bp.route('/rent/<int:days>/<int:id>')
def book_rent(days: int, id: int):
    """
    Функция аренды. Необходим VPN.

    merchant_id: from account in Fondy
    :param days: количество дней
    :param id: id книги
    :return: url transaction
    """
    book = Book.query.get(id)  # get book.id from database

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(book.price) + '00'
    }
    url = checkout.url(data).get('checkout_url')

    user_id = flask_login.current_user.id
    status = 'rent'
    end_rent = (datetime.datetime.utcnow() + datetime.timedelta(days=days))
    new_order = Order(status=status, user_id=user_id, book=book, end_rent=end_rent)
    db.session.add(new_order)
    db.session.commit()
    return redirect(url)


@bp.route('/reed/<int:id>', methods=['GET'])
@login_required
def reed(id):
    book = db.session.query(Book).get(id)
    text = os.path.abspath(os.path.join(os.path.dirname(__file__), 'books_files', book.filename))

    with io.open(text, encoding='utf-8') as file:
        return render_template('read.html', data=book, text=file.readlines())


# @bp.route('/admin', methods=['GET', 'POST'])
# @basic_auth.required
# def secret_view():
#     return render_template('secret.html')


@bp.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response
