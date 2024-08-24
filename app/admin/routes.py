import os
from app.models import Book, Order, User
from flask import render_template, redirect, request, url_for, session, flash
from app.admin import bp
from app import db
import sqlalchemy as sa
from app.admin.forms import EmptyForm
from sqlalchemy import column
from flask import flash, redirect, url_for, jsonify
from sqlalchemy import select

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

classes = {
    'user': User,
    'book': Book,
    'order': Order
}


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login function"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.index'))
        else:
            flash('Неверный пароль!', 'danger')
    return render_template('admin/login.html')


@bp.route('/logout')
def logout():
    """Logout function"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


@bp.route('/')
def index():
    """The function of the main page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    total_books = Book.query.count()
    total_users = User.query.count()
    total_orders = Order.query.count()
    return render_template('admin/index.html', books=total_books, users=total_users, orders=total_orders)


@bp.route('/users')
def users():
    """User Page function"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    sort_by = request.args.get('sort', 'id')  # Получение параметра сортировки из URL
    if sort_by not in ['id', 'username', 'email', 'telegram', 'password_hash', 'last_seen']:
        sort_by = 'id'
    users_list = User.query.order_by(getattr(User, sort_by)).all()  # Сортировка по выбранному полю
    return render_template('admin/users.html', users=users_list)


@bp.route('/orders')
def orders():
    """The function of the order page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    form = EmptyForm()
    sort_by = request.args.get('sort', 'id')  # Получение параметра сортировки из URL
    if sort_by not in ['id', 'status', 'start_rent', 'end_rent', 'user_id', 'book']:
        sort_by = 'id'
    orders_list = Order.query.order_by(getattr(Order, sort_by)).all()  # Сортировка по выбранному полю
    return render_template('admin/orders.html', orders=orders_list, form=form)


@bp.route('/books')
def books():
    """Book page function"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    sort_by = request.args.get('sort', 'id')  # Получение параметра сортировки из URL
    if sort_by not in ['id', 'name', 'price', 'category', 'author', 'year']:
        sort_by = 'id'
    books_list = Book.query.order_by(getattr(Book, sort_by)).all()  # Сортировка по выбранному полю
    return render_template('admin/books.html', books=books_list)


@bp.route('/delete/<string:object>/<int:id_object>')
def delete(object, id_object):
    """Record deletion function"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Determining which model to use based on the object parameter
    model_class = classes.get(object)
    if model_class is None:
        flash("Функция удаления такого объекта еще не реализована", "error")
        return redirect(url_for(f'admin.{object}s'))

    # Getting a record by id
    obj = db.session.scalar(
        select(model_class).where(model_class.id == id_object)
    )

    if obj is None:
        flash("Запись не найдена, хоть это и не возможно", "error")
    else:
        db.session.delete(obj)
        db.session.commit()
        flash("Запись удалена")
    return redirect(url_for(f'admin.{object}s'))


@bp.route('/edit/book/<int:id_object>', methods=['POST'])
def edit_book(id_object):
    """Handle book editing via AJAX"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Получаем запись по id
    book = db.session.scalar(
        select(Book).where(Book.id == id_object)
    )

    if book is None:
        return jsonify({"error": "Книга не найдена"}), 404

    # Обновляем данные
    book.name = request.form.get('name')
    book.price = request.form.get('price')
    book.category = request.form.get('category')
    book.author = request.form.get('author')
    book.year = request.form.get('year')
    book.image_link = request.form.get('image_link')
    book.filename = request.form.get('filename')

    db.session.commit()
    return jsonify({"success": "Книга обновлена"}), 200


@bp.route('/book/<int:id_object>', methods=['GET'])
def get_book(id_object):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Получаем запись по id
    book = db.session.scalar(
        select(Book).where(Book.id == id_object)
    )

    if book is None:
        return jsonify({"error": "Книга не найдена"}), 404

    return jsonify({
        "id": book.id,
        "name": book.name,
        "price": book.price,
        "category": book.category,
        "author": book.author,
        "year": book.year,
        "image_link": book.image_link,
        "filename": book.filename
    }), 200


@bp.route('/edit/order/<int:id_object>', methods=['POST'])
def edit_order(id_object):
    """Handle order editing via AJAX"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Получаем запись по id
    order = db.session.scalar(
        select(Order).where(Order.id == id_object)
    )

    if order is None:
        return jsonify({"error": "Заказ не найден"}), 404

    # Обновляем данные
    order.status = request.form.get('status')
    order.start_rent = request.form.get('start_rent')
    order.end_rent = request.form.get('end_rent')

    db.session.commit()
    return jsonify({"success": "Заказ обовлен"}), 200
    
@bp.route('/order/<int:id_object>', methods=['GET'])
def get_order(id_object):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Получаем запись по id
    order = db.session.scalar(
        select(Order).where(Order.id == id_object)
    )

    if order is None:
        return jsonify({"error": "Заказ не найден"}), 404

    return jsonify({
        "id": order.id,
        "status": order.status,
        "start_rent": order.start_rent,
        "end_rent": order.end_rent
    }), 200
