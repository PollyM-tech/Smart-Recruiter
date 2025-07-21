from flask_restful import Resource
from models import IntervieewProfile

class IntervieewProfileResource(Resource):
    def get(self, id=None):
        if id is None:
            profiles = IntervieewProfile.query.all()
            return [profile.to_dict() for profile in profiles], 200 
            
        else:
          profile = IntervieewProfile.query.filter_by(id=id).first()
          if profile:
             return profile.to_dict(), 200
          return {"error": "Feedback not found"}, 404
