"""
Test script for the CV-to-Job Matching System

This script tests the functionality of all components of the system:
1. CV Parser
2. Job Description Parser
3. Matching Algorithm
4. Feedback System
5. Integration of all components
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system modules
from cv_parser import CVParser
from job_description_parser import JobDescriptionParser
from matching_algorithm import MatchingAlgorithm
from feedback_system import FeedbackSystem

class TestCVToJobMatchingSystem(unittest.TestCase):
    """Test cases for the CV-to-Job Matching System."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cv_parser = CVParser()
        self.job_parser = JobDescriptionParser()
        self.matcher = MatchingAlgorithm()
        self.feedback_system = FeedbackSystem()
        
        # Sample CV text
        self.sample_cv_text = """
        John Doe
        Email: john.doe@example.com
        Phone: (123) 456-7890
        
        SUMMARY
        Experienced software engineer with 5 years of experience in Python development,
        machine learning, and web application development. Proficient in Python, JavaScript,
        and SQL. Master's degree in Computer Science from Stanford University.
        
        SKILLS
        Programming Languages: Python, JavaScript, SQL, Java
        Frameworks: Django, Flask, React, Node.js
        Tools: Git, Docker, AWS, TensorFlow
        
        EXPERIENCE
        Senior Software Engineer | ABC Tech | 2020 - Present
        - Developed and maintained Python web applications using Django and Flask
        - Implemented machine learning models for data analysis
        - Led a team of 3 junior developers
        
        Software Engineer | XYZ Solutions | 2018 - 2020
        - Built RESTful APIs using Node.js and Express
        - Developed front-end interfaces with React
        - Collaborated with cross-functional teams
        
        EDUCATION
        Master of Science in Computer Science | Stanford University | 2018
        Bachelor of Science in Computer Engineering | MIT | 2016
        """
        
        # Sample job description
        self.sample_job_description = """
        Senior Python Developer
        
        About the Role:
        We are looking for a Senior Python Developer to join our team. This is a full-time position
        based in San Francisco with hybrid work options.
        
        Responsibilities:
        - Design and implement high-quality Python code for our backend systems
        - Collaborate with cross-functional teams to define and implement new features
        - Optimize application performance and scalability
        - Write unit tests and integration tests
        - Mentor junior developers and conduct code reviews
        
        Requirements:
        - 5+ years of experience with Python development
        - Strong knowledge of Django or Flask frameworks
        - Experience with RESTful APIs and microservices architecture
        - Familiarity with AWS or other cloud platforms
        - Understanding of database systems (SQL and NoSQL)
        - Experience with version control systems (Git)
        - Bachelor's degree in Computer Science or related field
        
        Our Culture:
        We offer a collaborative and inclusive work environment where innovation is encouraged.
        We provide competitive compensation, health benefits, and opportunities for professional growth.
        """
        
        # Create a temporary CV file
        self.temp_cv_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        with open(self.temp_cv_file.name, 'w') as f:
            f.write(self.sample_cv_text)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_cv_file.name):
            os.remove(self.temp_cv_file.name)
    
    def test_cv_parser(self):
        """Test CV parser functionality."""
        # Mock the text extraction to return our sample CV text
        with patch.object(CVParser, '_extract_text_from_file', return_value=self.sample_cv_text):
            cv_data = self.cv_parser.parse_cv(self.temp_cv_file.name)
            
            # Check if basic information is extracted
            self.assertIsNotNone(cv_data)
            self.assertIn('text', cv_data)
            self.assertIn('skills', cv_data)
            
            # Check if skills are extracted
            self.assertIn('Python', cv_data['skills'])
            self.assertIn('JavaScript', cv_data['skills'])
            self.assertIn('SQL', cv_data['skills'])
            
            # Check if education is extracted
            self.assertTrue(any('Stanford' in edu for edu in cv_data.get('education', [])))
            
            # Check if experience is extracted
            self.assertTrue('experience' in cv_data or 'work_experience' in cv_data)
    
    def test_job_description_parser(self):
        """Test job description parser functionality."""
        job_data = self.job_parser.parse_job_description(self.sample_job_description)
        
        # Check if basic information is extracted
        self.assertIsNotNone(job_data)
        self.assertIn('text', job_data)
        self.assertIn('required_skills', job_data)
        
        # Check if skills are extracted
        self.assertIn('Python', job_data['required_skills'])
        self.assertIn('Django', job_data['required_skills']) or self.assertIn('Flask', job_data['required_skills'])
        
        # Check if experience requirements are extracted
        self.assertIn('experience_requirements', job_data)
        self.assertEqual(job_data['experience_requirements'].get('years'), 5)
        
        # Check if education requirements are extracted
        self.assertIn('education_requirements', job_data)
        self.assertTrue(any('Bachelor' in edu for edu in job_data['education_requirements']))
        
        # Check if responsibilities are extracted
        self.assertIn('responsibilities', job_data)
        self.assertTrue(len(job_data['responsibilities']) > 0)
    
    def test_matching_algorithm(self):
        """Test matching algorithm functionality."""
        # Mock the CV and job data
        cv_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '123-456-7890',
            'skills': ['Python', 'Django', 'Flask', 'JavaScript', 'SQL', 'Git'],
            'education': [
                'Master of Science in Computer Science, Stanford University',
                'Bachelor of Science in Computer Engineering, MIT'
            ],
            'text': 'Experienced software engineer with 5 years of experience in Python development.'
        }
        
        job_data = {
            'job_title': 'Senior Python Developer',
            'required_skills': ['Python', 'Django', 'Flask', 'AWS', 'SQL'],
            'experience_requirements': {
                'years': 5,
                'level': 'senior',
                'description': ['5+ years of experience with Python development']
            },
            'education_requirements': [
                'Bachelor\'s degree in Computer Science or related field'
            ],
            'responsibilities': [
                'Design and implement high-quality Python code',
                'Collaborate with cross-functional teams'
            ],
            'text': 'We are looking for a Senior Python Developer with 5+ years of experience.'
        }
        
        # Calculate match
        match_result = self.matcher.calculate_match(cv_data, job_data)
        
        # Check if match result is valid
        self.assertIsNotNone(match_result)
        self.assertIn('overall_match', match_result)
        self.assertIn('components', match_result)
        
        # Check if components are present
        self.assertIn('skills', match_result['components'])
        self.assertIn('experience', match_result['components'])
        self.assertIn('education', match_result['components'])
        
        # Check if scores are within valid range
        self.assertGreaterEqual(match_result['overall_match'], 0)
        self.assertLessEqual(match_result['overall_match'], 100)
        
        # Check if skills matching works
        skills_component = match_result['components']['skills']
        self.assertIn('matched', skills_component)
        self.assertIn('missing', skills_component)
        
        # Python, Django, Flask, and SQL should be matched
        matched_skills = [skill.lower() for skill in skills_component['matched'].get('exact', [])]
        self.assertIn('python', matched_skills)
        self.assertTrue('django' in matched_skills or 'flask' in matched_skills)
        self.assertIn('sql', matched_skills)
    
    def test_feedback_system(self):
        """Test feedback system functionality."""
        # Mock match result
        match_result = {
            'overall_match': 75.5,
            'components': {
                'skills': {
                    'score': 80.0,
                    'weight': 0.35,
                    'matched': {
                        'exact': ['Python', 'SQL', 'Django'],
                        'semantic': [
                            {'job_skill': 'AWS', 'cv_skill': 'Cloud Computing', 'similarity': 0.85}
                        ]
                    },
                    'missing': ['Flask']
                },
                'experience': {
                    'score': 90.0,
                    'weight': 0.30,
                    'details': {
                        'required_years': 5,
                        'cv_years': 5,
                        'required_level': 'senior',
                        'gap': 0
                    }
                },
                'education': {
                    'score': 100.0,
                    'weight': 0.20,
                    'details': {
                        'cv_degree_level': 'master',
                        'required_degree_level': 'bachelor',
                        'meets_requirements': True
                    }
                },
                'overall_similarity': {
                    'score': 70.0,
                    'weight': 0.15
                }
            }
        }
        
        # Mock CV and job data
        cv_data = {
            'name': 'John Doe',
            'skills': ['Python', 'SQL', 'Django', 'Cloud Computing'],
            'education': ['Master of Science in Computer Science']
        }
        
        job_data = {
            'job_title': 'Senior Python Developer',
            'required_skills': ['Python', 'SQL', 'Django', 'Flask', 'AWS']
        }
        
        # Generate feedback
        feedback_report = self.feedback_system.generate_feedback(match_result, cv_data, job_data)
        
        # Check if feedback report is valid
        self.assertIsNotNone(feedback_report)
        self.assertIn('overall_match', feedback_report)
        self.assertIn('match_category', feedback_report)
        self.assertIn('summary', feedback_report)
        self.assertIn('component_feedback', feedback_report)
        self.assertIn('recommendations', feedback_report)
        
        # Check if component feedback is present
        self.assertIn('skills', feedback_report['component_feedback'])
        self.assertIn('experience', feedback_report['component_feedback'])
        self.assertIn('education', feedback_report['component_feedback'])
        
        # Check if recommendations are present
        self.assertTrue(len(feedback_report['recommendations']) > 0)
        
        # Generate reports in different formats
        text_report = self.feedback_system.generate_report(feedback_report, format='text')
        html_report = self.feedback_system.generate_report(feedback_report, format='html')
        json_report = self.feedback_system.generate_report(feedback_report, format='json')
        
        # Check if reports are generated
        self.assertIsNotNone(text_report)
        self.assertIsNotNone(html_report)
        self.assertIsNotNone(json_report)
        
        # Check if HTML report contains HTML tags
        self.assertIn('<!DOCTYPE html>', html_report)
        self.assertIn('</html>', html_report)
        
        # Check if JSON report is valid JSON
        try:
            json_data = json.loads(json_report)
            self.assertEqual(json_data['overall_match'], feedback_report['overall_match'])
        except json.JSONDecodeError:
            self.fail("JSON report is not valid JSON")
    
    def test_integration(self):
        """Test integration of all components."""
        # Mock the text extraction to return our sample CV text
        with patch.object(CVParser, '_extract_text_from_file', return_value=self.sample_cv_text):
            # Parse CV
            cv_data = self.cv_parser.parse_cv(self.temp_cv_file.name)
            
            # Parse job description
            job_data = self.job_parser.parse_job_description(self.sample_job_description)
            
            # Calculate match
            match_result = self.matcher.calculate_match(cv_data, job_data)
            
            # Generate feedback
            feedback_report = self.feedback_system.generate_feedback(match_result, cv_data, job_data)
            
            # Generate report
            report = self.feedback_system.generate_report(feedback_report, format='text')
            
            # Check if the entire pipeline works
            self.assertIsNotNone(cv_data)
            self.assertIsNotNone(job_data)
            self.assertIsNotNone(match_result)
            self.assertIsNotNone(feedback_report)
            self.assertIsNotNone(report)
            
            # Check if the match score is within a reasonable range
            self.assertGreaterEqual(match_result['overall_match'], 0)
            self.assertLessEqual(match_result['overall_match'], 100)
            
            # Check if feedback contains recommendations
            self.assertTrue(len(feedback_report['recommendations']) > 0)

if __name__ == '__main__':
    unittest.main()
