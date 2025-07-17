from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from flask import Flask
from flask_restful import Api
from models import db
from datetime import datetime, timezone
from jwt_config import jwt_blocklist

from resources.user import LoginResource
from resources.user import SignupResource
from resources.user import UserListResource
from resources.user import LogoutResource
from resources.assessments import AssessmentResource


# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
api = Api(app)


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["SQLALCHEMY_ECHO"] = True

migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, allow_origins="*")


db.init_app(app)

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blocklist

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {
        "error": "The token has expired",
        "message": "Please log in again"
    }, 401

@app.route("/")
def index():
    return {"message": "Welcome to smart recruiter"}, 200




api.add_resource(LoginResource, "/login")
api.add_resource(SignupResource, "/signup")
api.add_resource(UserListResource, "/users")
api.add_resource(LogoutResource, "/logout")
api.add_resource(AssessmentResource, "/assessments", "/assessments/<int:assessment_id>")

if __name__ == "__main__":
    app.run(debug=True)

