from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os

from models import db
from resources.user import LoginResource, SignupResource, UserListResource
from resources.assessments import AssessmentResource
from resources.Questions import QuestionDetailResource, QuestionsListResource
from resources.results import IntervieweeResultsResource, ResultReleaseResource, ResultCreateOrUpdateResource
from resources.feedback import FeedbackResource
from resources.profile import ProfileResource
from resources.Submission import SubmissionListResource, SubmissionDetailResource
from resources.invites import InviteListResource, InviteResource, InviteAcceptanceResource

# Load environment variables
load_dotenv()

# Initialize app and extensions
app = Flask(__name__)
api = Api(app)

# App configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["SQLALCHEMY_ECHO"] = True

# Mail configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
mail = Mail(app)

# Routes
@app.route("/")
def index():
    return {"message": "Welcome to smart recruiter"}, 200

# API resources
api.add_resource(LoginResource, "/login")
api.add_resource(SignupResource, "/signup")
api.add_resource(UserListResource, "/users")
api.add_resource(AssessmentResource, "/assessments", "/assessments/<int:assessment_id>")
api.add_resource(SubmissionListResource, "/submissions")
api.add_resource(SubmissionDetailResource, "/submissions/<int:submission_id>")
api.add_resource(QuestionsListResource, "/assessments/<int:assessment_id>/questions")
api.add_resource(QuestionDetailResource, "/questions/<int:id>")
api.add_resource(FeedbackResource, "/feedback", "/feedback/<int:id>")
api.add_resource(ProfileResource, "/profile", "/profile/<id>")
api.add_resource(InviteListResource, "/invites")
api.add_resource(InviteResource, "/invites/<int:invite_id>")
api.add_resource(InviteAcceptanceResource, "/invites/accept/<string:token>")
api.add_resource(IntervieweeResultsResource, "/interviewee/results")
api.add_resource(ResultReleaseResource, "/results/<int:result_id>/release")
api.add_resource(ResultCreateOrUpdateResource, "/results")

# Only run server in development
if __name__ == "__main__":
    app.run(debug=True)
