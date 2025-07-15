from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()


class User(db.Model,SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum("recruiter", "student", name="user_roles"), nullable=False)

class Assessment(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    published = db.Column(db.Boolean, default=False)
    time_limit = db.Column(db.Integer)

class Question(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    type = db.Column(db.Enum("multiple_choice", "subjective", "codekata", name="question_types"), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON)     
    answer_key = db.Column(db.Text)

class Submission(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers = db.Column(db.JSON)
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    grade = db.Column(db.Float)


class Feedback(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text)


class Invite(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    status = db.Column(db.Enum("pending", "accepted", "declined", name="invite_statuses"), default="pending")
    sent_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime)
    delivery_channel = db.Column(db.Text)
    token = db.Column(db.Text, unique=True)


class Result(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    score = db.Column(db.Float)
    time_taken = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    pass_status = db.Column(db.Boolean)
    is_released = db.Column(db.Boolean, default=False)
    feedback_summary = db.Column(db.Text)