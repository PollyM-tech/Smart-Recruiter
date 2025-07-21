from flask_restful import Resource

from models import Feedback, db

class FeedbackResource(Resource):
   

    def get(self, id=None):  
      if id is None:
        feedbacks = Feedback.query.all()
        return [feedback.to_dict() for feedback in feedbacks], 200  
      else:
        feedback = Feedback.query.filter_by(id=id).first()
        if feedback:
            return feedback.to_dict(), 200
        return {"error": "Feedback not found"}, 404

    