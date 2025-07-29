from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message
from flask import current_app
from models import db, User, Invites, Assessments
import os
import secrets

invite_parser = reqparse.RequestParser()
invite_parser.add_argument("assessment_id", type=int, required=True, help="Assessment ID is required")
invite_parser.add_argument("interviewee_email", type=str, required=True, help="Interviewee email is required")
invite_parser.add_argument("expires_in_days", type=int, default=7, help="Expiration in days (default: 7)")

class InviteResource(Resource):
    @jwt_required()
    def get(self, invite_id):
        current_user_id = int(get_jwt_identity())
        invite = Invites.query.get_or_404(invite_id)

        if invite.recruiter_id != current_user_id and invite.interviewee_id != current_user_id:
            return {"message": "Unauthorized"}, 403

        return invite.to_dict(), 200

class InviteListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = int(get_jwt_identity())
        invites = Invites.query.filter_by(recruiter_id=current_user_id).all()
        return [invite.to_dict() for invite in invites], 200

    @jwt_required()
    def post(self):
        current_user_id = int(get_jwt_identity())
        data = invite_parser.parse_args()

        recruiter = User.query.get(current_user_id)
        if not recruiter or recruiter.role != 'recruiter':
            return {"message": "Unauthorized"}, 403

        assessment = Assessments.query.filter_by(
            id=data['assessment_id'],
            creator_id=current_user_id
        ).first()

        if not assessment:
            return {"message": "Assessment not found or permission denied"}, 404

        interviewee = User.query.filter_by(
            email=data['interviewee_email'],
            role='interviewee'
        ).first()

        if not interviewee:
            return {"message": "Interviewee not found. Please ensure they are registered"}, 404

        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=data['expires_in_days'])

        invite = Invites(
            recruiter_id=current_user_id,
            interviewee_id=interviewee.id,
            assessment_id=assessment.id,
            status="pending",
            token=token,
            expires_at=expires_at,
            sent_at=datetime.utcnow()
        )

        db.session.add(invite)
        
        # Attempt to send email but commit invite regardless
        if os.getenv("MAIL_ENABLED", "true").lower() == "true":
            try:
                frontend_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
                invite_url = f"{frontend_url}/invites/accept?token={token}"

                subject = "Assessment Invitation"
                body = f"""
Hello {interviewee.name},

You have been invited to participate in an assessment: {assessment.title}.

Click below to accept the invitation:
{invite_url}

This invitation will expire on {expires_at.strftime('%Y-%m-%d %H:%M UTC')}.

Best regards,  
{recruiter.name}
                """

                msg = Message(subject=subject, recipients=[interviewee.email], body=body)
                current_app.extensions["mail"].send(msg)
            except Exception as e:
                current_app.logger.error(f"Email failed: {str(e)}")
        
        db.session.commit()

        # Return invite with additional interviewee_email field
        return {
            "message": "Invite created successfully",
            "invite": {
                **invite.to_dict(),
                "interviewee_email": interviewee.email
            }
        }, 201

class InviteAcceptanceResource(Resource):
    @jwt_required()
    def patch(self, token):
        current_user_id = int(get_jwt_identity())
        invite = Invites.query.filter_by(token=token).first()
        
        if not invite:
            return {"message": "Invalid invitation token"}, 404
        if invite.interviewee_id != current_user_id:
            return {"message": "You are not authorized to accept this invite"}, 403
        if invite.status != "pending":
            return {"message": "This invitation has already been processed"}, 400
        if datetime.utcnow() > invite.expires_at:
            return {"message": "This invitation has expired"}, 400

        invite.status = "accepted"
        invite.accepted_at = datetime.utcnow()
        db.session.commit()

        return {
            "message": "Invitation accepted successfully",
            "assessment_id": invite.assessment_id
        }, 200