import flask_login
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import os
import io

from app import app, db
from app.models import User, Book, Order

# for pay
from cloudipsp import Api, Checkout


@app.route('/', methods=['GET'])
def index():
    return render_template('public/index.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('public/about.html')


@app.route('/about_private', methods=['GET'])
def about_private():
    return render_template('private/about_private.html')


@app.route('/main', methods=['GET'])
@login_required
def main():
    books = Book.query.order_by(Book.price).all()
    return render_template('private/main.html', data=books)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Функция входа"""
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # next_page = request.args.get('next')
            # return redirect(next_page)
            return redirect('/main')
        else:
            flash('Некорректный логин или пароль')
    else:
        # flash('Пожалуйста заполните все поля')
        pass

    return render_template('public/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Функция регистрации"""
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Заполните все поля!')
        elif password != password2:
            flash('Пароли должны совпадать')
        else:
            try:
                hash_pwd = generate_password_hash(password)
                new_user = User(login=login, password=hash_pwd)
                db.session.add(new_user)
                db.session.commit()
            except IntegrityError:
                flash('Логин занят')
                return redirect(url_for('register'))

            return redirect(url_for('login_page'))

    return render_template('public/register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


@app.errorhandler(404)
def error404(error):
    """Функция-обработчик ошибки отсутствия страницы"""
    return render_template('404.html')


@app.route('/None', methods=['GET'])
@login_required
def none_page():
    """Функция-обработчик отсутствующей страницы перенаправления"""
    return render_template('private/main.html')


@app.route('/buy/<int:id>')
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


@app.route('/rent/<int:days>/<int:id>')
def book_rent(days: int, id: int):
    """
    Функция аренды. Необходим VPN.

    merchant_id: from account in Fondy
    :param days: количество дней
    :param id: id книги
    :return: url transaction
    """
    book = Book.query.get(id)  # get book.id from database
    rent_price = book.price / 100 * days
    print(rent_price)
    print(type(rent_price))

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(int(rent_price)) + '00'
    }
    url = checkout.url(data).get('checkout_url')

    user_id = flask_login.current_user.id
    book_id = id
    status = 'rent'
    new_order = Order(user_id=user_id, books=book_id, status=status)
    db.session.add(new_order)
    db.session.commit()
    return redirect(url)


@app.route('/box', methods=['GET'])
@login_required
def box():
    data = flask_login.current_user.orders
    return render_template('private/box.html', data=data)


@app.route('/reed/<int:id>', methods=['GET'])
@login_required
def reed(id):
    book = db.session.query(Book).get(id)
    text = os.path.abspath(os.path.join(os.path.dirname(__file__), 'books_files', book.filename))

    with io.open(text, encoding='utf-8') as file:
        return render_template('private/reed.html', data=book, text=file.readlines())
