# resources/submission.py

from flask_restful import Resource
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Submissions

class SubmissionListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        submissions = Submissions.query.filter_by(user_id=user_id).all()
        return [s.to_dict() for s in submissions], 200
    
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        assessment_id = data.get("assessment_id")
        answers = data.get("answers")

        if not assessment_id or not answers:
            return {"error": "assessment_id and answers are required"}, 400

        submission = Submissions(
            user_id=user_id,
            assessment_id=assessment_id,
            answers=answers,
            submitted_at=datetime.utcnow(),
            grade=None
        )

        db.session.add(submission)
        db.session.commit()

        return {
            "message": "Submission successful",
            "submission_id": submission.id
        }, 201