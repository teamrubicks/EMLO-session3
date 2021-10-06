import os

from dotenv import load_dotenv

from flask import Flask

from src import error_handlers

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.register_blueprint(error_handlers.blueprint)

from src.routes import routes
