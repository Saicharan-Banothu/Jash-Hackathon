import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class MedicalTestAnalyzer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.target_column = ''
        
    def load_data(self, csv_file_path):
        """Load and preprocess medical test data from CSV"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            print(f"Loaded data with shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Identify numeric and categorical columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            print(f"Numeric columns: {numeric_cols}")
            print(f"Categorical columns: {categorical_cols}")
            
            # For simplicity, let's assume the last column is the target (condition to predict)
            self.target_column = df.columns[-1]
            self.feature_columns = df.columns[:-1].tolist()
            
            # Prepare features
            X = df[self.feature_columns].copy()
            y = df[self.target_column].copy()
            
            # Handle categorical variables
            for col in categorical_cols:
                if col in self.feature_columns:
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col].astype(str))
                    self.label_encoders[col] = le
            
            # Handle missing values
            X = X.fillna(X.mean())
            
            # Scale numeric features
            if len(numeric_cols) > 0:
                X[numeric_cols] = self.scaler.fit_transform(X[numeric_cols])
            
            # Encode target variable
            self.label_encoders['target'] = LabelEncoder()
            y_encoded = self.label_encoders['target'].fit_transform(y)
            
            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X, y_encoded)
            
            # Save model
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_columns': self.feature_columns,
                'target_column': self.target_column
            }, 'medical_model.pkl')
            
            print("Model trained and saved successfully!")
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict(self, test_data):
        """Predict condition based on test results"""
        try:
            if self.model is None:
                # Try to load saved model
                if os.path.exists('medical_model.pkl'):
                    model_data = joblib.load('medical_model.pkl')
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    self.label_encoders = model_data['label_encoders']
                    self.feature_columns = model_data['feature_columns']
                    self.target_column = model_data['target_column']
                else:
                    return "Model not trained", 0.0
            
            # Prepare input data
            input_df = pd.DataFrame([test_data])
            
            # Encode categorical variables
            for col in self.feature_columns:
                if col in self.label_encoders:
                    if test_data[col] in self.label_encoders[col].classes_:
                        input_df[col] = self.label_encoders[col].transform([test_data[col]])[0]
                    else:
                        input_df[col] = 0  # Default value for unknown categories
                else:
                    # Handle numeric columns
                    input_df[col] = float(test_data[col])
            
            # Scale features
            numeric_cols = input_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                input_df[numeric_cols] = self.scaler.transform(input_df[numeric_cols])
            
            # Make prediction
            prediction = self.model.predict(input_df[self.feature_columns])[0]
            probability = np.max(self.model.predict_proba(input_df[self.feature_columns]))
            
            # Decode prediction
            condition = self.label_encoders['target'].inverse_transform([prediction])[0]
            
            return condition, round(probability * 100, 2)
            
        except Exception as e:
            return f"Prediction error: {str(e)}", 0.0
    
    def analyze_medical_report(self, test_results):
        """Comprehensive analysis of medical report"""
        try:
            # Predict condition
            condition, confidence = self.predict(test_results)
            
            # Generate recommendations based on prediction
            recommendations = self.generate_recommendations(condition, test_results)
            
            # Generate analysis summary
            analysis = f"""
            Based on the provided test results:
            - Predicted Condition: {condition}
            - Confidence Level: {confidence}%
            - Key Findings: {self.get_key_findings(test_results)}
            """
            
            return {
                'condition': condition,
                'confidence': confidence,
                'analysis': analysis.strip(),
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'condition': 'Unknown',
                'confidence': 0,
                'analysis': f'Analysis error: {str(e)}',
                'recommendations': 'Please consult with a healthcare professional.'
            }
    
    def generate_recommendations(self, condition, test_results):
        """Generate personalized recommendations"""
        base_recommendations = {
            'Normal': 'Maintain current lifestyle with regular checkups.',
            'Diabetes': 'Monitor blood sugar levels regularly. Consult endocrinologist.',
            'Hypertension': 'Reduce salt intake. Monitor blood pressure daily.',
            'Anemia': 'Increase iron-rich foods. Consider supplements.',
            'Hyperthyroidism': 'Consult endocrinologist for thyroid function tests.',
            'Kidney Disease': 'Reduce protein intake. Monitor kidney function.',
            'Liver Disease': 'Avoid alcohol. Monitor liver enzymes regularly.'
        }
        
        recommendation = base_recommendations.get(condition, 
            'Consult with a healthcare professional for personalized advice.')
        
        # Add specific recommendations based on test values
        specific_advice = []
        for test, value in test_results.items():
            if 'glucose' in test.lower() and float(value) > 126:
                specific_advice.append('High glucose detected - consider dietary changes.')
            elif 'pressure' in test.lower() and float(value) > 140:
                specific_advice.append('Elevated blood pressure - monitor regularly.')
            elif 'cholesterol' in test.lower() and float(value) > 200:
                specific_advice.append('High cholesterol - consider dietary modifications.')
        
        if specific_advice:
            recommendation += ' ' + ' '.join(specific_advice)
        
        return recommendation
    
    def get_key_findings(self, test_results):
        """Identify key abnormal findings"""
        abnormal_findings = []
        
        # Define normal ranges (simplified - adjust based on your CSV)
        normal_ranges = {
            'glucose': (70, 100),
            'blood_pressure': (90, 120),
            'cholesterol': (0, 200),
            'hemoglobin': (12, 16)
        }
        
        for test, value in test_results.items():
            for key, (low, high) in normal_ranges.items():
                if key in test.lower():
                    try:
                        num_value = float(value)
                        if num_value < low or num_value > high:
                            abnormal_findings.append(f"{test}: {value} (outside normal range)")
                    except ValueError:
                        continue
        
        return ', '.join(abnormal_findings) if abnormal_findings else 'No significant abnormalities detected'