import flask_login
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db
from app.models import User, Book, Box


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


@app.route('/box', methods=['GET'])
@login_required
def box():
    a = Box.query.all()
    return render_template('private/box.html', data=a)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')

            return redirect(next_page)
        else:
            flash('Некорректный логин или пароль')
    else:
        # flash('Пожалуйста заполните все поля')
        pass

    return render_template('public/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
    return render_template('404.html')


@app.route('/None', methods=['GET'])
@login_required
def none_page():
    return render_template('private/main.html')
