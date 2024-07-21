from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from flask_admin import Admin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Im the key, honey.'
db = SQLAlchemy(app)
manager = LoginManager(app)
admin = Admin(app, name='Admin', template_mode='bootstrap4')

from app import models, routes
