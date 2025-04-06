"""
Test script for the deployed CV-to-Job Matching System website.
This script performs basic functionality tests on the deployed website.
"""

import requests
import os
import time
import argparse
from pathlib import Path

def test_website_availability(base_url):
    """Test if the website is available and responding."""
    print(f"Testing website availability at {base_url}...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Website is available and responding")
            return True
        else:
            print(f"❌ Website returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to website: {e}")
        return False

def test_cv_analysis(base_url, cv_file_path, job_description):
    """Test CV analysis functionality."""
    print("\nTesting CV analysis functionality...")
    
    if not os.path.exists(cv_file_path):
        print(f"❌ CV file not found at {cv_file_path}")
        return False
    
    try:
        # Prepare the files and data for the request
        files = {'cv_file': open(cv_file_path, 'rb')}
        data = {'job_description': job_description}
        
        # Send the request
        response = requests.post(f"{base_url}/analyze", files=files, data=data)
        
        # Close the file
        files['cv_file'].close()
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ CV analysis successful with match percentage: {result.get('match_percentage')}%")
                
                # Test report URL
                report_url = result.get('report_url')
                if report_url:
                    report_response = requests.get(f"{base_url}{report_url}")
                    if report_response.status_code == 200:
                        print("✅ Report generation successful")
                    else:
                        print(f"❌ Failed to access report: Status code {report_response.status_code}")
                
                return True
            else:
                print(f"❌ CV analysis failed: {result.get('error')}")
                return False
        else:
            print(f"❌ CV analysis request failed with status code {response.status_code}")
            try:
                error = response.json().get('error', 'Unknown error')
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text[:100]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send CV analysis request: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during CV analysis test: {e}")
        return False

def test_api_endpoint(base_url, cv_file_path, job_description):
    """Test the API endpoint."""
    print("\nTesting API endpoint...")
    
    if not os.path.exists(cv_file_path):
        print(f"❌ CV file not found at {cv_file_path}")
        return False
    
    try:
        # Prepare the files and data for the request
        files = {'cv_file': open(cv_file_path, 'rb')}
        data = {'job_description': job_description}
        
        # Send the request
        response = requests.post(f"{base_url}/api/analyze", files=files, data=data)
        
        # Close the file
        files['cv_file'].close()
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ API endpoint working with match percentage: {result.get('match_percentage')}%")
                return True
            else:
                print(f"❌ API request failed: {result.get('error')}")
                return False
        else:
            print(f"❌ API request failed with status code {response.status_code}")
            try:
                error = response.json().get('error', 'Unknown error')
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text[:100]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send API request: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during API test: {e}")
        return False

def run_all_tests(base_url, cv_file_path, job_description):
    """Run all tests and return overall result."""
    print("=" * 50)
    print(f"TESTING CV-TO-JOB MATCHING SYSTEM AT {base_url}")
    print("=" * 50)
    
    # Test website availability
    availability_result = test_website_availability(base_url)
    
    if not availability_result:
        print("\n❌ Website is not available. Skipping remaining tests.")
        return False
    
    # Test CV analysis
    analysis_result = test_cv_analysis(base_url, cv_file_path, job_description)
    
    # Test API endpoint
    api_result = test_api_endpoint(base_url, cv_file_path, job_description)
    
    # Overall result
    overall_result = availability_result and analysis_result and api_result
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Website Availability: {'✅ PASS' if availability_result else '❌ FAIL'}")
    print(f"CV Analysis: {'✅ PASS' if analysis_result else '❌ FAIL'}")
    print(f"API Endpoint: {'✅ PASS' if api_result else '❌ FAIL'}")
    print("-" * 50)
    print(f"Overall Result: {'✅ PASS' if overall_result else '❌ FAIL'}")
    print("=" * 50)
    
    return overall_result

def create_sample_cv():
    """Create a sample CV file for testing if none is provided."""
    sample_cv_path = "sample_cv.txt"
    
    sample_cv_content = """
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
    
    with open(sample_cv_path, "w") as f:
        f.write(sample_cv_content)
    
    print(f"Created sample CV file at {sample_cv_path}")
    return sample_cv_path

def create_sample_job_description():
    """Create a sample job description for testing."""
    return """
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
    """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the deployed CV-to-Job Matching System website")
    parser.add_argument("--url", default="https://cv-job-matching.onrender.com", help="Base URL of the deployed website")
    parser.add_argument("--cv", help="Path to a CV file for testing")
    parser.add_argument("--job", help="Job description for testing")
    
    args = parser.parse_args()
    
    # Use provided CV file or create a sample one
    cv_file_path = args.cv if args.cv else create_sample_cv()
    
    # Use provided job description or create a sample one
    job_description = args.job if args.job else create_sample_job_description()
    
    # Run all tests
    run_all_tests(args.url, cv_file_path, job_description)
