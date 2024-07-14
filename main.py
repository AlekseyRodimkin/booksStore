from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

# for pay
from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = f'sqlite:///shop.db'

db = SQLAlchemy(app)


# Database - Table - data
# Table:
# _____________________________________________________________
# | id   title   price   category   author   year   isActive |
# | 1    string  int     string     string   int    bool     |
# -------------------------------------------------------------

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50))
    year = db.Column(db.Integer)
    isActive = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return self.title


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        category = request.form['category']
        author = request.form['author']
        year = request.form['year']
        item = Item(title=title, price=price, category=category, author=author, year=year)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return render_template('error.html')
    else:
        return render_template('create.html')


@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id) # get book.id from database
    order_number = 'get order_number from new db for shop doks'

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": item.price
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
