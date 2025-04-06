"""
CV-to-Job Matching System Web Interface

This module provides a web interface for the CV-to-Job Matching System.
It allows users to upload CVs, input job descriptions, and view compatibility ratings and feedback.
"""

import os
import tempfile
import uuid
import logging
from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import system modules
from cv_parser import CVParser
from job_description_parser import JobDescriptionParser
from matching_algorithm import MatchingAlgorithm
from feedback_system import FeedbackSystem
from database import get_db

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', str(uuid.uuid4()))

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize system components
cv_parser = CVParser()
job_parser = JobDescriptionParser()
matcher = MatchingAlgorithm()
feedback_system = FeedbackSystem()
db = get_db()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process CV and job description, return match results."""
    # Check if CV file was uploaded
    if 'cv_file' not in request.files:
        return jsonify({'error': 'No CV file uploaded'}), 400
    
    cv_file = request.files['cv_file']
    if cv_file.filename == '':
        return jsonify({'error': 'No CV file selected'}), 400
    
    if not allowed_file(cv_file.filename):
        return jsonify({'error': f'CV file type not allowed. Please upload one of: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Get job description
    job_description = request.form.get('job_description', '')
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400
    
    # Save CV file
    filename = secure_filename(cv_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cv_file.save(file_path)
    
    try:
        # Parse CV
        cv_data = cv_parser.parse_cv(file_path)
        
        # Parse job description
        job_data = job_parser.parse_job_description(job_description)
        
        # Calculate match
        match_result = matcher.calculate_match(cv_data, job_data)
        
        # Generate feedback
        feedback_report = feedback_system.generate_feedback(match_result, cv_data, job_data)
        
        # Generate HTML report
        html_report = feedback_system.generate_report(feedback_report, format='html')
        
        # Save HTML report
        report_filename = f"report_{uuid.uuid4()}.html"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        with open(report_path, 'w') as f:
            f.write(html_report)
        
        # Save analysis to database
        job_title = job_data.get('job_title', 'Unknown Position')
        analysis_id = db.save_analysis(
            cv_filename=filename,
            job_title=job_title,
            match_percentage=match_result['overall_match'],
            feedback_report=feedback_report
        )
        
        logger.info(f"Analysis completed and saved with ID: {analysis_id}")
        
        # Return results
        return jsonify({
            'success': True,
            'match_percentage': match_result['overall_match'],
            'report_url': f'/reports/{report_filename}',
            'analysis_id': analysis_id,
            'summary': feedback_report['summary'],
            'feedback': feedback_report
        })
    
    except Exception as e:
        logger.error(f"Error processing analysis: {str(e)}")
        return jsonify({'error': f'Error processing files: {str(e)}'}), 500
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/reports/<filename>')
def get_report(filename):
    """Serve generated reports."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for CV-to-job matching."""
    # Check if CV file was uploaded
    if 'cv_file' not in request.files:
        return jsonify({'error': 'No CV file uploaded'}), 400
    
    cv_file = request.files['cv_file']
    if cv_file.filename == '':
        return jsonify({'error': 'No CV file selected'}), 400
    
    if not allowed_file(cv_file.filename):
        return jsonify({'error': f'CV file type not allowed. Please upload one of: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Get job description
    job_description = request.form.get('job_description', '')
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400
    
    # Save CV file to temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        cv_file.save(temp.name)
        temp_path = temp.name
    
    try:
        # Parse CV
        cv_data = cv_parser.parse_cv(temp_path)
        
        # Parse job description
        job_data = job_parser.parse_job_description(job_description)
        
        # Calculate match
        match_result = matcher.calculate_match(cv_data, job_data)
        
        # Generate feedback
        feedback_report = feedback_system.generate_feedback(match_result, cv_data, job_data)
        
        # Return JSON results
        return jsonify({
            'success': True,
            'match_percentage': match_result['overall_match'],
            'feedback': feedback_report
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing files: {str(e)}'}), 500
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
