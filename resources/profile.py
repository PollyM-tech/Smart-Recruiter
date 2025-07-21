from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import IntervieewProfile, User, db
from datetime import datetime

class IntervieewProfileResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help="Name is required")
    parser.add_argument("interview_number", type=int, required=True, help="Interview number is required")
    parser.add_argument("company", type=str, required=True, help="Company is required")
    parser.add_argument("role", type=str, required=True, help="Role is required")
    parser.add_argument("date", type=str, required=True, help="Date is required in YYYY-MM-DD format")
    parser.add_argument("time", type=str, required=True, help="Time is required in HH:MM format")
    parser.add_argument("location", type=str, required=True, help="Location is required")
    parser.add_argument("grade", type=float, required=False, help="Grade is required")

    def get(self, id=None):
        if id is None:
            profiles = IntervieewProfile.query.all()
            return [profile.to_dict() for profile in profiles], 200 
            
        else:
          profile = IntervieewProfile.query.filter_by(id=id).first()
          if profile:
             return profile.to_dict(), 200
          return {"error": "Feedback not found"}, 404
        
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != "recruiter":
            return {"error": "Unauthorized. Only recruiters can create profiles."}, 403

        data = IntervieewProfileResource.parser.parse_args()

        # Convert date and time strings to proper datetime objects
        try:
            date_obj = datetime.strptime(data["date"], "%Y-%m-%d").date()
            time_obj = datetime.strptime(data["time"], "%H:%M").time()
        except ValueError:
            return {"error": "Invalid date or time format"}, 400

        profile = IntervieewProfile(
            name=data["name"],
            interview_number=data["interview_number"],
            company=data["company"],
            role=data["role"],
            date=date_obj,
            time=time_obj,
            location=data["location"],
            grade=data["grade"]
        )

        db.session.add(profile)
        db.session.commit()

        return profile.to_dict(), 201
