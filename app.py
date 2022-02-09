from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import config
import os


app = Flask(__name__)
app.config.from_mapping(SQLALCHEMY_DATABASE_URI=config.POSTGRES_URI, SQLALCHEMY_TRACK_MODIFICATIONS=False)
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
