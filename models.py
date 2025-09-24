from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Medical history relationship
    medical_reports = db.relationship('MedicalReport', backref='user', lazy=True)

class MedicalReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_name = db.Column(db.String(200), nullable=False)
    test_data = db.Column(db.Text, nullable=False)  # JSON string of test results
    analysis_result = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_name': self.report_name,
            'test_data': json.loads(self.test_data),
            'analysis_result': self.analysis_result,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }