from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

app = Flask(__name__) # Start Flask app
app.config.from_object(Config)
db = SQLAlchemy(app) # Setup database
migrate = Migrate(app, db) # Setup migration engine
login = LoginManager(app) # Set up login, initilaized and created
login.login_view = 'login'

from app import routes