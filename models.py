from app import db
from datetime import datetime

class InterviewQuestion(db.Model):
    """Model for storing interview questions"""
    __tablename__ = 'interview_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    questions = db.Column(db.Text, nullable=False)  # JSON string of questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<InterviewQuestion {self.id}: {self.job_title}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'job_title': self.job_title,
            'job_description': self.job_description,
            'questions': self.questions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }