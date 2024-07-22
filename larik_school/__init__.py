from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"
app.config["SECRET_KEY"] = 'daflkjie25kj3l1k'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from larik_school import routes