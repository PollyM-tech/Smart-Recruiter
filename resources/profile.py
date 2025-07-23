from flask_restful import Resource, reqparse, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Profile, User, db
from datetime import datetime

def nullable_str(value):
    return value if value not in (None, '', 'null') else None

class ProfileResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=False)
    parser.add_argument("company", type=str, required=False)
    parser.add_argument("role", type=str, required=False)
    parser.add_argument("location", type=nullable_str, required=False)
    parser.add_argument("skills", type=nullable_str, required=False)
    parser.add_argument("education", type=nullable_str, required=False)
    parser.add_argument("experience", type=nullable_str, required=False)

    def get(self, id=None):
        if id is None:
            profiles = Profile.query.all()
            return [profile.to_dict() for profile in profiles], 200 
            
        else:
          profile = Profile.query.filter_by(id=id).first()
          if profile:
             return profile.to_dict(), 200
          return {"error": "Feedback not found"}, 404
        
    @jwt_required()
    def post(self):
        # Identify logged-in user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {"error": "Unauthorized. User not found."}, 404

        data = self.parser.parse_args()

        # Create a profile for the logged-in user only
        profile = Profile(
            user_id=current_user_id,
            name=data.get("name"),
            company=data.get("company"),
            role=data.get("role"),
            location=data.get("location"),
            skills=data.get("skills"),
            education=data.get("education"),
            experience=data.get("experience")
        )

        db.session.add(profile)
        db.session.commit()

        return profile.to_dict(), 201

    @jwt_required()
    def patch(self, id):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        profile = Profile.query.get(id)
        if not profile:
            return {"error": "Profile not found"}, 404

        # Only allow recruiters to edit any profile
        # Interviewees can only edit their own
        if user.role != "recruiter" and profile.user_id != current_user_id:
            return {"error": "Unauthorized. You can only edit your own profile."}, 403

        data = ProfileResource.parser.parse_args()

        # Update fields if provided
        if data["name"] is not None:
            profile.name = data["name"]
        if data["company"] is not None:
            profile.company = data["company"]
        if data["role"] is not None:
            profile.role = data["role"]
        if data["location"] is not None:
            profile.location = data["location"]
        if data["skills"] is not None:
            profile.skills = data["skills"]
        if data["education"] is not None:
            profile.education = data["education"]
        if data["experience"] is not None:
            profile.experience = data["experience"]

        db.session.commit()
        return profile.to_dict(), 200