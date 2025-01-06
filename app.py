from flask import Flask, request, jsonify, render_template
import numpy as np
from joblib import load
from flask_cors import CORS
import os
from sklearn.metrics import mean_squared_error, r2_score

app = Flask(__name__)
CORS(app)

def load_model():
    try:
        # Try multiple possible paths for the model file
        possible_paths = [
            # Absolute path
            os.path.join(
                'D:', 'IUBAT', 'Machine Learning with Python',
                'MachineLearningWithPython-main', 'Sessions', 'Day12',
                'linear_regression_model_multiple.joblib'
            ),
            # Relative path
            'linear_regression_model_multiple.joblib',
            # Current directory
            os.path.join(os.path.dirname(__file__), 'linear_regression_model_multiple.joblib')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found model at: {path}")
                model = load(path)
                print("Model loaded successfully!")
                return model
                
        raise FileNotFoundError("Model file not found in any of the expected locations")
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

model = load_model()

def make_prediction(input_data):
    try:
        if model is None:
            raise Exception("Model not loaded")
            
        # Convert input data to numeric values
        features = np.array([[
            1 if input_data['smoker'] == 'yes' else 0,
            float(input_data['age']),
            float(input_data['bmi']),
            int(input_data['children']),
            1 if input_data['sex'] == 'male' else 0,
            1 if input_data['region'] == 'northeast' else 0,
            1 if input_data['region'] == 'northwest' else 0,
            1 if input_data['region'] == 'southeast' else 0,
            1 if input_data['region'] == 'southwest' else 0
        ]])
        
        # Make prediction
        prediction = model.predict(features)
        return float(prediction[0])
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({'success': False, 'error': 'Model not loaded. Please check if the model file exists.'})
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No input data provided'})
            
        prediction = make_prediction(data)
        if prediction is not None:
            return jsonify({
                'success': True, 
                'prediction': prediction,
                'model_metrics': {
                    'r2_score': 0.7836,  # From your notebook
                    'rmse': 5796.28      # From your notebook
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Prediction failed'})
    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    if model is None:
        print("WARNING: Model failed to load. Please check if the model file exists and is accessible.")
    app.run(debug=True)