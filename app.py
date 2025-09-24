from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'medreport-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medreport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app, origins=["http://localhost:8000"], supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    medical_reports = db.relationship('MedicalReport', backref='user', lazy=True)

class MedicalReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_name = db.Column(db.String(200), nullable=False)
    test_data = db.Column(db.Text, nullable=False)
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Simple Rule-Based Medical Analyzer
class MedicalAnalyzer:
    def __init__(self):
        self.normal_ranges = {
            'glucose': (70, 100),
            'blood_pressure': (90, 120),
            'systolic': (90, 120),
            'diastolic': (60, 80),
            'cholesterol': (0, 200),
            'heart_rate': (60, 100),
            'bmi': (18.5, 24.9),
            'hemoglobin': (12, 16),
            'wbc': (4.5, 11.0),
            'rbc': (4.5, 6.0)
        }
    
    def analyze(self, test_results):
        abnormalities = []
        conditions = []
        
        # Analyze each test
        for test_name, value in test_results.items():
            test_name_lower = test_name.lower()
            
            # Find matching range
            for range_key, (low, high) in self.normal_ranges.items():
                if range_key in test_name_lower:
                    try:
                        num_value = float(value)
                        if num_value < low:
                            abnormalities.append(f"{test_name} is LOW ({value})")
                            conditions.append(self.get_condition(test_name_lower, 'low'))
                        elif num_value > high:
                            abnormalities.append(f"{test_name} is HIGH ({value})")
                            conditions.append(self.get_condition(test_name_lower, 'high'))
                        else:
                            abnormalities.append(f"{test_name} is NORMAL ({value})")
                    except ValueError:
                        abnormalities.append(f"{test_name}: {value} (could not analyze)")
                    break
        
        # Determine overall condition
        if not conditions:
            overall_condition = "Normal"
            confidence = 95
        else:
            overall_condition = ", ".join(set(conditions))
            confidence = 85 - (len(conditions) * 5)
        
        analysis = self.generate_analysis(abnormalities, overall_condition)
        recommendations = self.generate_recommendations(overall_condition, abnormalities)
        
        return {
            'condition': overall_condition,
            'confidence': max(confidence, 50),
            'abnormalities': abnormalities,
            'analysis': analysis,
            'recommendations': recommendations
        }
    
    def get_condition(self, test_name, status):
        condition_map = {
            'glucose': {'high': 'Pre-diabetes', 'low': 'Hypoglycemia'},
            'blood_pressure': {'high': 'Hypertension', 'low': 'Hypotension'},
            'systolic': {'high': 'Hypertension', 'low': 'Hypotension'},
            'diastolic': {'high': 'Hypertension', 'low': 'Hypotension'},
            'cholesterol': {'high': 'High Cholesterol'},
            'bmi': {'high': 'Overweight', 'low': 'Underweight'}
        }
        
        for key, conditions in condition_map.items():
            if key in test_name:
                return conditions.get(status, 'Abnormal')
        
        return 'Requires medical attention'
    
    def generate_analysis(self, abnormalities, condition):
        normal_count = sum(1 for ab in abnormalities if 'NORMAL' in ab)
        abnormal_count = len(abnormalities) - normal_count
        
        if abnormal_count == 0:
            return "All test results are within normal ranges. Excellent health indicators!"
        else:
            abnormal_list = [ab for ab in abnormalities if 'NORMAL' not in ab]
            return f"Analysis shows {abnormal_count} abnormal finding(s): {', '.join(abnormal_list)}. Suggested condition: {condition}."
    
    def generate_recommendations(self, condition, abnormalities):
        recommendations = {
            'Normal': 'Maintain your current healthy lifestyle with regular checkups.',
            'Hypertension': 'Reduce sodium intake, exercise regularly, monitor blood pressure daily, and consult a cardiologist.',
            'Pre-diabetes': 'Monitor carbohydrate intake, increase physical activity, and get regular blood sugar checks.',
            'High Cholesterol': 'Reduce saturated fats, increase fiber intake, exercise regularly, and consider statins if recommended.',
            'Overweight': 'Focus on balanced diet with portion control, regular exercise, and lifestyle changes.',
            'Underweight': 'Increase calorie intake with nutrient-dense foods, strength training, and medical consultation.',
            'Hypoglycemia': 'Eat regular meals, monitor blood sugar, and carry emergency glucose.',
            'Abnormal': 'Consult with a healthcare professional for comprehensive evaluation.',
            'Requires medical attention': 'Seek immediate medical consultation for proper diagnosis.'
        }
        
        base_recommendation = recommendations.get(condition, recommendations['Abnormal'])
        
        # Add specific advice
        specific_advice = []
        for ab in abnormalities:
            ab_lower = ab.lower()
            if 'glucose' in ab_lower and 'high' in ab_lower:
                specific_advice.append('Limit sugar and refined carbohydrates.')
            elif 'blood_pressure' in ab_lower and 'high' in ab_lower:
                specific_advice.append('Practice stress management techniques.')
            elif 'cholesterol' in ab_lower and 'high' in ab_lower:
                specific_advice.append('Increase omega-3 fatty acids intake.')
            elif 'bmi' in ab_lower and 'high' in ab_lower:
                specific_advice.append('Aim for gradual weight loss through diet and exercise.')
        
        if specific_advice:
            base_recommendation += ' Additional advice: ' + '. '.join(specific_advice)
        
        return base_recommendation

# Initialize analyzer
analyzer = MedicalAnalyzer()

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            age=data.get('age'),
            gender=data.get('gender')
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.password == data['password']:
            login_user(user)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'age': user.age,
                    'gender': user.gender
                }
            }), 200
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@app.route('/api/analyze-report', methods=['POST'])
@login_required
def analyze_report():
    try:
        data = request.get_json()
        test_results = data.get('test_results', {})
        report_name = data.get('report_name', 'Medical Report')
        
        if not test_results:
            return jsonify({'success': False, 'error': 'No test data provided'}), 400
        
        analysis = analyzer.analyze(test_results)
        
        # Save to database
        report = MedicalReport(
            user_id=current_user.id,
            report_name=report_name,
            test_data=json.dumps(test_results),
            analysis_result=analysis['analysis'],
            recommendations=analysis['recommendations']
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'report_id': report.id
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/report-history', methods=['GET'])
@login_required
def get_history():
    try:
        reports = MedicalReport.query.filter_by(user_id=current_user.id)\
            .order_by(MedicalReport.timestamp.desc()).all()
        
        return jsonify({
            'success': True,
            'reports': [report.to_dict() for report in reports]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user-profile', methods=['GET'])
@login_required
def get_profile():
    user = current_user
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'gender': user.gender,
            'joined_date': user.created_at.isoformat()
        }
    })

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        user = current_user
        
        user.age = data.get('age', user.age)
        user.gender = data.get('gender', user.gender)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'MedReport Analyzer API'})

# Initialize database
with app.app_context():
    db.create_all()
    print("Database initialized!")

if __name__ == '__main__':
    app.run(debug=True, port=5000)