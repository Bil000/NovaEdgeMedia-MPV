from datetime import datetime
from sqlalchemy import JSON
from app import db


class Campaign(db.Model):
    __tablename__ = 'campaign'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(200), nullable=False)
    target_audience = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    objectives = db.Column(db.Text, nullable=False)
    channels = db.Column(db.String(500))
    current_metrics = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with reports
    reports = db.relationship('Report', backref='campaign', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_name': self.campaign_name,
            'target_audience': self.target_audience,
            'budget': self.budget,
            'duration': self.duration,
            'objectives': self.objectives,
            'channels': self.channels,
            'current_metrics': self.current_metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Report(db.Model):
    __tablename__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    report_data = db.Column(JSON, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'report_data': self.report_data,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }