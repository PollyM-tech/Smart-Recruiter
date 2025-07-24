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

    @jwt_required()
    def get(self, id=None):
        
        if id == "self":
            current_user_id = get_jwt_identity()
            profile = Profile.query.filter_by(user_id=current_user_id).first()
            if not profile:
                return {"error": "Profile not found"}, 404
            return profile.to_dict(), 200

        if id is None:
            profiles = Profile.query.all()
            return [profile.to_dict() for profile in profiles], 200
        
        profile = Profile.query.filter_by(id=id).first()
        if profile:
            return profile.to_dict(), 200
        return {"error": "Profile not found"}, 404
    
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
        if id == "self":
            profile = Profile.query.filter_by(user_id=current_user_id).first()
            if not profile:
                return {"error": "Profile not found"}, 404
        else:
          profile = Profile.query.get(id) 

        if not profile:
            return {"error": "Profile not found"}, 404

        # Only allow recruiters to edit any profile
        # Interviewees can only edit their own
        if user.role != "recruiter" and profile.user_id != current_user_id:
            return {"error": "Unauthorized. You can only edit your own profile."}, 403

        data = ProfileResource.parser.parse_args()

        for field, value in data.items():
            if value is not None:
                setattr(profile, field, value)

        db.session.commit()
        return profile.to_dict(), 200