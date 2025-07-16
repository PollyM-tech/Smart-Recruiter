from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin


db = SQLAlchemy()

class User(db.Model,SerializerMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(Enum("recruiter", "student", name="user_roles"), nullable=False)

    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)

    assessments = db.relationship("Assessments", back_populates="creator")
    submissions = db.relationship("Submissions", back_populates="user")
    feedback_given = db.relationship("Feedback", back_populates="recruiter")
    invites_sent = db.relationship("Invites", foreign_keys="Invites.recruiter_id", back_populates="recruiter")
    invites_received = db.relationship("Invites", foreign_keys="Invites.student_id", back_populates="student")
    
    serialize_rules = ("-password", "-assessments", "-submissions","-feedback_given","-invites_sent","-invites_received")
class Assessments(db.Model, SerializerMixin):
    __tablename__ = "assessments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    published = db.Column(db.Boolean)
    time_limit = db.Column(db.Integer)

    creator = db.relationship("User", back_populates="assessments")
    questions = db.relationship("Questions", back_populates="assessment")
    submissions = db.relationship("Submissions", back_populates="assessment")
    invites = db.relationship("Invites", back_populates="assessment")

class Questions(db.Model, SerializerMixin):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"))
    type = db.Column(Enum("multiple_choice", "codekata", name="question_types"), nullable=False)
    prompt = db.Column(db.Text)
    options = db.Column(db.JSON)
    answer_key = db.Column(db.Text)

    assessment = db.relationship("Assessments", back_populates="questions")
    feedback_entries = db.relationship("Feedback", back_populates="question")

class Submissions(db.Model, SerializerMixin):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    answers = db.Column(db.JSON)
    submitted_at = db.Column(db.DateTime)
    grade = db.Column(db.Float)

    assessment = db.relationship("Assessments", back_populates="submissions")
    user = db.relationship("User", back_populates="submissions")
    feedback = db.relationship("Feedback", back_populates="submission")
    result = db.relationship("Results", back_populates="submission", uselist=False)

class Feedback(db.Model, SerializerMixin):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment = db.Column(db.Text)

    question = db.relationship("Questions", back_populates="feedback_entries")
    submission = db.relationship("Submissions", back_populates="feedback")
    recruiter = db.relationship("User", back_populates="feedback_given")

class Invites(db.Model, SerializerMixin):
    __tablename__ = "invites"
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"))
    status = db.Column(Enum("pending", "accepted", "declined", name="invite_statuses"), default="pending")
    sent_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime)
    delivery_channel = db.Column(db.String)
    token = db.Column(db.String, unique=True)

    recruiter = db.relationship("User", foreign_keys=[recruiter_id], back_populates="invites_sent")
    student = db.relationship("User", foreign_keys=[student_id], back_populates="invites_received")
    assessment = db.relationship("Assessments", back_populates="invites")

class Results(db.Model, SerializerMixin):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    score = db.Column(db.Float)
    time_taken = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    pass_status = db.Column(db.Boolean)
    is_released = db.Column(db.Boolean, default=False)
    feedback_summary = db.Column(db.Text)

    submission = db.relationship("Submissions", back_populates="result")