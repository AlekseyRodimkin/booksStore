from app import app, db

if __name__ == '__main__':
    with app.app_context():
        """Создаст таблицы если их нет в базе"""
        db.create_all()

    app.run(debug=True)
