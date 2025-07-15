from flask import Flask
from flask_migrate import Migrate
from models import db
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)


    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smart_recruiter.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")


    db.init_app(app)
    Migrate(app, db)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
