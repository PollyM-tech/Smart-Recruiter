from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message
from models import db, User, Invites, Assessments
from app import mail
import os
import secrets

invite_parser = reqparse.RequestParser()
invite_parser.add_argument("assessment_id", type=int, required=True, help="Assessment ID is required")
invite_parser.add_argument("interviewee_email", type=str, required=True, help="Interviewee email is required")
invite_parser.add_argument('expires_in_days', type=int, default=7, help='Expiration in days (default: 7)')

class InviteListResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = invite_parser.parse_args()

        # Getting the recruiter
        recruiter = User.query.get(current_user_id)
        if not recruiter or recruiter.role != 'recruiter':
            return {"message": "Unauthorized"}, 403
        
        # Getting the assessment
        assessment = Assessments.query.filter_by(
            id=data['assessment_id'], 
            creator_id=current_user_id
        ).first()
        if not assessment:
            return {"message": "Assessment not found or permission denied"}, 404
        
        # Finding interviewee
        interviewee = User.query.filter_by(
            email=data['interviewee_email'], 
            role='interviewee'
        ).first()
        if not interviewee:
            return {"message": "Interviewee not found. Please ensure they are registered"}, 404
        
        # Generating token
        token = secrets.token_urlsafe(32)
        
        # Calculating expiration
        expires_in_days = data['expires_in_days']
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Creating invitation record
        invite = Invites(
            recruiter_id=current_user_id,
            interviewee_id=interviewee.id,
            assessment_id=assessment.id,
            status="pending",
            token=token,
            expires_at=expires_at,
            sent_at=datetime.utcnow()  # Add sent_at timestamp
        )
        db.session.add(invite)
        db.session.commit()

        # Sending email with invitation
        try:
            frontend_url = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')
            invite_url = f"{frontend_url}/invites/accept?token={token}"

            subject = "Assessment Invitation"
            # Improved email formatting
            body = f"""
Hello {interviewee.name},

You have been invited to participate in an assessment: {assessment.title}.

Please click the link below to accept the invitation:
{invite_url}

This invitation will expire on {expires_at.strftime('%Y-%m-%d %H:%M UTC')}.

Best regards,
{recruiter.name}
            """
            msg = Message(subject=subject, recipients=[interviewee.email], body=body)
            mail.send(msg)
            return {
                "message": "Invite sent successfully",
                "invite": {
                    "id": invite.id,
                    "token": token,
                    "expires_at": expires_at.isoformat()
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"message": f"Failed to send email. Please try again later: {str(e)}"}, 500