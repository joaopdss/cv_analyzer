"""
CV-to-Job Matching System - README

A system that analyzes CVs against job descriptions and provides compatibility ratings and feedback.
"""

# CV-to-Job Matching System

## Overview

The CV-to-Job Matching System is an AI-powered tool that analyzes CVs against job descriptions to determine compatibility and provide actionable feedback. The system focuses on tech jobs and uses advanced Natural Language Processing (NLP) techniques to extract information from both CVs and job descriptions, perform semantic matching, and generate detailed feedback reports.

## Features

- **Flexible Input**: Accepts CVs in various formats (PDF, DOCX, TXT) and job descriptions as text
- **Intelligent Parsing**: Uses NLP to extract key information from both CVs and job descriptions
- **Advanced Matching**: Compares CV details against job requirements using both keyword matching and semantic analysis
- **Customizable Scoring**: Calculates match scores with configurable weights for different components
- **Actionable Feedback**: Provides detailed reports with match scores, matched/missing skills, and recommendations

## System Architecture

The system consists of the following components:

1. **CV Parser**: Extracts structured information from CV documents
2. **Job Description Parser**: Extracts requirements and preferences from job descriptions
3. **Matching Algorithm**: Compares CV data with job requirements using semantic matching
4. **Feedback System**: Generates detailed feedback and recommendations
5. **Web Interface**: Provides a user-friendly interface for interacting with the system

## Technologies Used

- **Python**: Core programming language
- **Flask**: Web framework for the user interface
- **spaCy & NLTK**: NLP libraries for text processing
- **Sentence Transformers**: For semantic matching and similarity calculations
- **Bootstrap**: Frontend framework for responsive design

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/cv-job-matching.git
cd cv-job-matching
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Download required NLP models:
```
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords punkt
```

## Usage

1. Start the Flask application:
```
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Upload your CV and paste the job description

4. Click "Analyze Match" to get your compatibility rating and feedback

## API Usage

The system also provides an API endpoint for programmatic access:

```python
import requests

url = 'http://localhost:5000/api/analyze'
files = {'cv_file': open('your_cv.pdf', 'rb')}
data = {'job_description': 'Job description text...'}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Match Percentage: {result['match_percentage']}%")
print(f"Feedback: {result['feedback']}")
```

## Components

### CV Parser

The CV Parser extracts structured information from CV documents, including:
- Personal details (name, email, phone)
- Skills and technologies
- Education history
- Work experience
- Projects and achievements

### Job Description Parser

The Job Description Parser extracts key requirements from job postings, including:
- Required skills and technologies
- Experience requirements (years, roles, responsibilities)
- Education requirements
- Company culture indicators
- Job type and location

### Matching Algorithm

The Matching Algorithm compares CV data with job requirements using:
- Exact keyword matching for skills
- Semantic similarity for related terms
- Experience evaluation (years and relevance)
- Education assessment (degree level and field)
- Overall document similarity

### Feedback System

The Feedback System generates detailed reports including:
- Overall match percentage
- Component-specific scores (skills, experience, education)
- Lists of matched and missing skills
- Prioritized recommendations for improvement
- Multiple report formats (text, HTML, JSON)

## Testing

Run the test suite to verify all components are working correctly:

```
python -m unittest discover tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project uses various open-source libraries and models
- Special thanks to the spaCy, NLTK, and Sentence Transformers teams
