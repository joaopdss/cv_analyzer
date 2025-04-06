"""
Feedback System Module

This module generates detailed feedback and recommendations based on CV-to-job matching results.
It provides actionable insights to help users improve their CV for specific job positions.

The module is part of the CV-to-Job Matching System.
"""

import json
import numpy as np
from collections import defaultdict

class FeedbackSystem:
    """
    A class for generating detailed feedback and recommendations based on CV-to-job matching results.
    """
    
    def __init__(self):
        """
        Initialize the Feedback System.
        """
        # Define feedback templates
        self.templates = {
            'high_match': "Your CV shows a strong match for this position! You have {match_percentage}% compatibility with the job requirements.",
            'medium_match': "Your CV shows a moderate match for this position with {match_percentage}% compatibility. With some targeted improvements, you could significantly increase your chances.",
            'low_match': "Your CV currently has {match_percentage}% compatibility with this position. Consider the recommendations below to improve your match."
        }
        
        # Define threshold values for match categories
        self.thresholds = {
            'high': 80,
            'medium': 60,
            'low': 0
        }
    
    def generate_feedback(self, match_result, cv_data, job_data):
        """
        Generate detailed feedback and recommendations based on matching results.
        
        Args:
            match_result (dict): Results from the matching algorithm.
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            dict: Detailed feedback and recommendations.
        """
        overall_match = match_result['overall_match']
        
        # Determine match category
        match_category = self._get_match_category(overall_match)
        
        # Generate overall feedback
        overall_feedback = self.templates[match_category].format(match_percentage=overall_match)
        
        # Generate component-specific feedback
        skills_feedback = self._generate_skills_feedback(match_result, cv_data, job_data)
        experience_feedback = self._generate_experience_feedback(match_result, cv_data, job_data)
        education_feedback = self._generate_education_feedback(match_result, cv_data, job_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(match_result, cv_data, job_data)
        
        # Compile feedback report
        feedback_report = {
            'overall_match': overall_match,
            'match_category': match_category.replace('_', ' '),
            'summary': overall_feedback,
            'component_feedback': {
                'skills': skills_feedback,
                'experience': experience_feedback,
                'education': education_feedback
            },
            'recommendations': recommendations,
            'job_title': job_data.get('job_title', 'This position'),
            'match_details': match_result
        }
        
        return feedback_report
    
    def _get_match_category(self, match_percentage):
        """
        Determine the match category based on the overall match percentage.
        
        Args:
            match_percentage (float): Overall match percentage.
            
        Returns:
            str: Match category ('high_match', 'medium_match', or 'low_match').
        """
        if match_percentage >= self.thresholds['high']:
            return 'high_match'
        elif match_percentage >= self.thresholds['medium']:
            return 'medium_match'
        else:
            return 'low_match'
    
    def _generate_skills_feedback(self, match_result, cv_data, job_data):
        """
        Generate feedback on skills match.
        
        Args:
            match_result (dict): Results from the matching algorithm.
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            dict: Skills feedback.
        """
        skills_component = match_result['components']['skills']
        skills_score = skills_component['score']
        matched_skills = skills_component['matched']
        missing_skills = skills_component['missing']
        
        # Count matched skills
        exact_matches = len(matched_skills.get('exact', []))
        semantic_matches = len(matched_skills.get('semantic', []))
        total_matches = exact_matches + semantic_matches
        
        # Count required skills
        required_skills = job_data.get('required_skills', [])
        total_required = len(required_skills) if required_skills else 0
        
        # Generate feedback text
        if total_required == 0:
            feedback_text = "No specific skills were identified in the job description."
        elif skills_score >= 80:
            feedback_text = f"Your CV demonstrates strong alignment with the required skills for this position. You match {total_matches} out of {total_required} required skills ({skills_score}%)."
        elif skills_score >= 60:
            feedback_text = f"Your CV shows good alignment with many of the required skills. You match {total_matches} out of {total_required} required skills ({skills_score}%)."
        else:
            feedback_text = f"Your CV currently matches {total_matches} out of {total_required} required skills ({skills_score}%). Adding the missing skills to your CV would significantly improve your match."
        
        # Compile skills feedback
        skills_feedback = {
            'score': skills_score,
            'feedback': feedback_text,
            'matched_skills': {
                'exact': matched_skills.get('exact', []),
                'semantic': matched_skills.get('semantic', [])
            },
            'missing_skills': missing_skills
        }
        
        return skills_feedback
    
    def _generate_experience_feedback(self, match_result, cv_data, job_data):
        """
        Generate feedback on experience match.
        
        Args:
            match_result (dict): Results from the matching algorithm.
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            dict: Experience feedback.
        """
        experience_component = match_result['components']['experience']
        experience_score = experience_component['score']
        experience_details = experience_component['details']
        
        required_years = experience_details.get('required_years')
        cv_years = experience_details.get('cv_years')
        gap = experience_details.get('gap')
        
        # Generate feedback text
        if required_years is None:
            feedback_text = "No specific experience requirements were identified in the job description."
        elif cv_years is None:
            feedback_text = f"The job requires {required_years} years of experience, but we couldn't identify your years of experience from your CV. Consider clearly stating your years of experience."
        elif gap is None:
            feedback_text = f"The job requires {required_years} years of experience. We couldn't determine if there's a gap between your experience and the requirement."
        elif gap <= 0:
            feedback_text = f"Your experience ({cv_years} years) meets or exceeds the required experience ({required_years} years) for this position."
        else:
            feedback_text = f"The job requires {required_years} years of experience, but your CV indicates {cv_years} years. There's a gap of {gap} years."
        
        # Add relevance feedback
        if experience_score >= 80:
            relevance_feedback = "Your experience appears highly relevant to the job responsibilities."
        elif experience_score >= 60:
            relevance_feedback = "Your experience appears moderately relevant to the job responsibilities."
        else:
            relevance_feedback = "Your experience may not be closely aligned with the job responsibilities."
        
        feedback_text += " " + relevance_feedback
        
        # Compile experience feedback
        experience_feedback = {
            'score': experience_score,
            'feedback': feedback_text,
            'required_years': required_years,
            'your_years': cv_years,
            'gap': gap
        }
        
        return experience_feedback
    
    def _generate_education_feedback(self, match_result, cv_data, job_data):
        """
        Generate feedback on education match.
        
        Args:
            match_result (dict): Results from the matching algorithm.
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            dict: Education feedback.
        """
        education_component = match_result['components']['education']
        education_score = education_component['score']
        education_details = education_component['details']
        
        cv_degree = education_details.get('cv_degree_level')
        required_degree = education_details.get('required_degree_level')
        meets_requirements = education_details.get('meets_requirements', False)
        
        # Generate feedback text
        if required_degree is None:
            feedback_text = "No specific education requirements were identified in the job description."
        elif cv_degree is None:
            feedback_text = f"The job requires a {required_degree} degree, but we couldn't identify your education level from your CV. Consider clearly stating your education."
        elif meets_requirements:
            feedback_text = f"Your education ({cv_degree}) meets or exceeds the required education ({required_degree}) for this position."
        else:
            feedback_text = f"The job requires a {required_degree} degree, but your CV indicates a {cv_degree} degree. Consider highlighting any additional qualifications or relevant experience to compensate."
        
        # Compile education feedback
        education_feedback = {
            'score': education_score,
            'feedback': feedback_text,
            'required_degree': required_degree,
            'your_degree': cv_degree,
            'meets_requirements': meets_requirements
        }
        
        return education_feedback
    
    def _generate_recommendations(self, match_result, cv_data, job_data):
        """
        Generate actionable recommendations to improve CV match.
        
        Args:
            match_result (dict): Results from the matching algorithm.
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            list: Actionable recommendations.
        """
        recommendations = []
        
        # Skills recommendations
        skills_component = match_result['components']['skills']
        missing_skills = skills_component['missing']
        
        if missing_skills:
            if len(missing_skills) <= 3:
                skills_rec = f"Add the following skills to your CV: {', '.join(missing_skills)}."
            else:
                top_skills = missing_skills[:3]
                skills_rec = f"Add key missing skills to your CV, especially: {', '.join(top_skills)}."
            recommendations.append({
                'category': 'skills',
                'recommendation': skills_rec,
                'priority': 'high'
            })
        
        # Experience recommendations
        experience_component = match_result['components']['experience']
        experience_details = experience_component['details']
        gap = experience_details.get('gap')
        
        if gap is not None and gap > 0:
            experience_rec = f"Highlight any additional experience that might not be clearly stated in your CV. The job requires {experience_details['required_years']} years of experience."
            recommendations.append({
                'category': 'experience',
                'recommendation': experience_rec,
                'priority': 'medium'
            })
        
        # Education recommendations
        education_component = match_result['components']['education']
        education_details = education_component['details']
        meets_requirements = education_details.get('meets_requirements', False)
        
        if not meets_requirements and education_details.get('required_degree') is not None:
            education_rec = f"Emphasize any additional certifications, training, or relevant projects that compensate for the difference between your education level and the required {education_details['required_degree']} degree."
            recommendations.append({
                'category': 'education',
                'recommendation': education_rec,
                'priority': 'medium'
            })
        
        # General recommendations
        if match_result['overall_match'] < 70:
            # Keyword optimization
            recommendations.append({
                'category': 'keywords',
                'recommendation': "Optimize your CV with keywords from the job description, especially in your summary and work experience sections.",
                'priority': 'high'
            })
            
            # Tailor CV
            recommendations.append({
                'category': 'tailoring',
                'recommendation': "Tailor your CV to highlight experiences and achievements most relevant to this specific position.",
                'priority': 'medium'
            })
        
        # Add quantifiable achievements recommendation if score is medium
        if 50 <= match_result['overall_match'] < 80:
            recommendations.append({
                'category': 'achievements',
                'recommendation': "Add more quantifiable achievements to your work experience to demonstrate impact (e.g., 'Increased sales by 20%' rather than 'Responsible for sales').",
                'priority': 'medium'
            })
        
        # If no recommendations were generated, add a general one
        if not recommendations:
            recommendations.append({
                'category': 'general',
                'recommendation': "Your CV is well-matched to this position. Consider adding more specific achievements and metrics to strengthen your application further.",
                'priority': 'low'
            })
        
        return recommendations
    
    def generate_report(self, feedback_report, format='text'):
        """
        Generate a formatted report from the feedback data.
        
        Args:
            feedback_report (dict): Feedback data.
            format (str): Output format ('text', 'html', or 'json').
            
        Returns:
            str: Formatted report.
        """
        if format == 'json':
            return json.dumps(feedback_report, indent=2)
        elif format == 'html':
            return self._generate_html_report(feedback_report)
        else:  # Default to text
            return self._generate_text_report(feedback_report)
    
    def _generate_text_report(self, feedback_report):
        """
        Generate a text report from the feedback data.
        
        Args:
            feedback_report (dict): Feedback data.
            
        Returns:
            str: Text report.
        """
        report = []
        
        # Add header
        report.append("=" * 80)
        report.append(f"CV MATCH REPORT FOR: {feedback_report['job_title']}")
        report.append("=" * 80)
        
        # Add overall match
        report.append(f"\nOVERALL MATCH: {feedback_report['overall_match']}% ({feedback_report['match_category']})")
        report.append("\nSUMMARY:")
        report.append(feedback_report['summary'])
        
        # Add component feedback
        report.append("\nDETAILED FEEDBACK:")
        
        # Skills feedback
        skills = feedback_report['component_feedback']['skills']
        report.append(f"\n1. SKILLS (Score: {skills['score']}%)")
        report.append(f"   {skills['feedback']}")
        
        if skills['matched_skills']['exact']:
            report.append("\n   Matched Skills:")
            for skill in skills['matched_skills']['exact']:
                report.append(f"   - {skill}")
        
        if skills['matched_skills']['semantic']:
            report.append("\n   Similar Skills:")
            for match in skills['matched_skills']['semantic']:
                report.append(f"   - {match['job_skill']} (similar to your skill: {match['cv_skill']})")
        
        if skills['missing_skills']:
            report.append("\n   Missing Skills:")
            for skill in skills['missing_skills']:
                report.append(f"   - {skill}")
        
        # Experience feedback
        experience = feedback_report['component_feedback']['experience']
        report.append(f"\n2. EXPERIENCE (Score: {experience['score']}%)")
        report.append(f"   {experience['feedback']}")
        
        # Education feedback
        education = feedback_report['component_feedback']['education']
        report.append(f"\n3. EDUCATION (Score: {education['score']}%)")
        report.append(f"   {education['feedback']}")
        
        # Add recommendations
        report.append("\nRECOMMENDATIONS:")
        
        # Group recommendations by priority
        priority_groups = defaultdict(list)
        for rec in feedback_report['recommendations']:
            priority_groups[rec['priority']].append(rec)
        
        # Add recommendations by priority
        for priority in ['high', 'medium', 'low']:
            if priority_groups[priority]:
                report.append(f"\n{priority.upper()} PRIORITY:")
                for i, rec in enumerate(priority_groups[priority], 1):
                    report.append(f"   {i}. {rec['recommendation']}")
        
        return "\n".join(report)
    
    def _generate_html_report(self, feedback_report):
        """
        Generate an HTML report from the feedback data.
        
        Args:
            feedback_report (dict): Feedback data.
            
        Returns:
            str: HTML report.
        """
        html = []
        
        # Start HTML document
        html.append('<!DOCTYPE html>')
        html.append('<html lang="en">')
        html.append('<head>')
        html.append('    <meta charset="UTF-8">')
        html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append('    <title>CV Match Report</title>')
        html.append('    <style>')
        html.append('        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }')
        html.append('        h1, h2, h3 { color: #333; }')
        html.append('        .header { text-align: center; margin-bottom: 30px; }')
        html.append('        .match-score { font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; }')
        html.append('        .high { color: #28a745; }')
        html.append('        .medium { color: #ffc107; }')
        html.append('        .low { color: #dc3545; }')
        html.append('        .section { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }')
        html.append('        .section-title { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px; }')
        html.append('        .skill-list { display: flex; flex-wrap: wrap; }')
        html.append('        .skill-item { background: #f8f9fa; padding: 5px 10px; margin: 5px; border-radius: 3px; }')
        html.append('        .missing-skill { background: #fff3cd; }')
        html.append('        .recommendation { padding: 10px; margin-bottom: 10px; border-left: 4px solid #ddd; }')
        html.append('        .high-priority { border-left-color: #dc3545; }')
        html.append('        .medium-priority { border-left-color: #ffc107; }')
        html.append('        .low-priority { border-left-color: #28a745; }')
        html.append('    </style>')
        html.append('</head>')
        html.append('<body>')
        
        # Header
        html.append('    <div class="header">')
        html.append(f'        <h1>CV Match Report</h1>')
        html.append(f'        <h2>{feedback_report["job_title"]}</h2>')
        html.append('    </div>')
        
        # Overall match
        match_class = 'high' if feedback_report['overall_match'] >= 80 else ('medium' if feedback_report['overall_match'] >= 60 else 'low')
        html.append(f'    <div class="match-score {match_class}">')
        html.append(f'        Overall Match: {feedback_report["overall_match"]}% ({feedback_report["match_category"]})')
        html.append('    </div>')
        
        # Summary
        html.append('    <div class="section">')
        html.append('        <h3 class="section-title">Summary</h3>')
        html.append(f'        <p>{feedback_report["summary"]}</p>')
        html.append('    </div>')
        
        # Skills feedback
        skills = feedback_report['component_feedback']['skills']
        html.append('    <div class="section">')
        html.append('        <h3 class="section-title">Skills Assessment</h3>')
        html.append(f'        <p><strong>Score: {skills["score"]}%</strong></p>')
        html.append(f'        <p>{skills["feedback"]}</p>')
        
        if skills['matched_skills']['exact']:
            html.append('        <h4>Matched Skills</h4>')
            html.append('        <div class="skill-list">')
            for skill in skills['matched_skills']['exact']:
                html.append(f'            <div class="skill-item">{skill}</div>')
            html.append('        </div>')
        
        if skills['matched_skills']['semantic']:
            html.append('        <h4>Similar Skills</h4>')
            html.append('        <div class="skill-list">')
            for match in skills['matched_skills']['semantic']:
                html.append(f'            <div class="skill-item">{match["job_skill"]} (similar to: {match["cv_skill"]})</div>')
            html.append('        </div>')
        
        if skills['missing_skills']:
            html.append('        <h4>Missing Skills</h4>')
            html.append('        <div class="skill-list">')
            for skill in skills['missing_skills']:
                html.append(f'            <div class="skill-item missing-skill">{skill}</div>')
            html.append('        </div>')
        
        html.append('    </div>')
        
        # Experience feedback
        experience = feedback_report['component_feedback']['experience']
        html.append('    <div class="section">')
        html.append('        <h3 class="section-title">Experience Assessment</h3>')
        html.append(f'        <p><strong>Score: {experience["score"]}%</strong></p>')
        html.append(f'        <p>{experience["feedback"]}</p>')
        html.append('    </div>')
        
        # Education feedback
        education = feedback_report['component_feedback']['education']
        html.append('    <div class="section">')
        html.append('        <h3 class="section-title">Education Assessment</h3>')
        html.append(f'        <p><strong>Score: {education["score"]}%</strong></p>')
        html.append(f'        <p>{education["feedback"]}</p>')
        html.append('    </div>')
        
        # Recommendations
        html.append('    <div class="section">')
        html.append('        <h3 class="section-title">Recommendations</h3>')
        
        # Group recommendations by priority
        priority_groups = defaultdict(list)
        for rec in feedback_report['recommendations']:
            priority_groups[rec['priority']].append(rec)
        
        # Add recommendations by priority
        for priority in ['high', 'medium', 'low']:
            if priority_groups[priority]:
                html.append(f'        <h4>{priority.capitalize()} Priority</h4>')
                for rec in priority_groups[priority]:
                    html.append(f'        <div class="recommendation {priority}-priority">')
                    html.append(f'            <p>{rec["recommendation"]}</p>')
                    html.append('        </div>')
        
        html.append('    </div>')
        
        # End HTML document
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)

# Example usage
if __name__ == "__main__":
    # Create feedback system instance
    feedback_system = FeedbackSystem()
    
    # Example match result
    match_result = {
        'overall_match': 75.5,
        'components': {
            'skills': {
                'score': 80.0,
                'weight': 0.35,
                'matched': {
                    'exact': ['Python', 'SQL', 'Machine Learning'],
                    'semantic': [
                        {'job_skill': 'Deep Learning', 'cv_skill': 'Machine Learning', 'similarity': 0.85}
                    ]
                },
                'missing': ['PyTorch']
            },
            'experience': {
                'score': 90.0,
                'weight': 0.30,
                'details': {
                    'required_years': 3,
                    'cv_years': 5,
                    'required_level': 'senior',
                    'gap': -2
                }
            },
            'education': {
                'score': 100.0,
                'weight': 0.20,
                'details': {
                    'cv_degree_level': 'master',
                    'required_degree_level': 'master',
                    'meets_requirements': True
                }
            },
            'overall_similarity': {
                'score': 70.0,
                'weight': 0.15
            }
        }
    }
    
    # Example CV data
    cv_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '123-456-7890',
        'skills': ['Python', 'Machine Learning', 'Data Analysis', 'SQL', 'TensorFlow'],
        'education': [
            'Master of Science in Computer Science, Stanford University',
            'Bachelor of Science in Mathematics, MIT'
        ],
        'text': 'Experienced data scientist with 5 years of experience in machine learning and data analysis. Proficient in Python, SQL, and TensorFlow. Master of Science in Computer Science from Stanford University.'
    }
    
    # Example job description data
    job_data = {
        'job_title': 'Senior Data Scientist',
        'required_skills': ['Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'SQL'],
        'experience_requirements': {
            'years': 3,
            'level': 'senior',
            'description': ['Minimum 3 years of experience in machine learning or related field']
        },
        'education_requirements': [
            'Master\'s degree in Computer Science, Statistics, or related field'
        ],
        'responsibilities': [
            'Develop and implement machine learning models',
            'Analyze large datasets to extract insights',
            'Collaborate with cross-functional teams'
        ],
        'text': 'We are looking for a Senior Data Scientist with strong experience in machine learning and data analysis. The ideal candidate will have at least 3 years of experience and a Master\'s degree in Computer Science or related field. Proficiency in Python, Machine Learning, Deep Learning, PyTorch, and SQL is required.'
    }
    
    # Generate feedback
    feedback_report = feedback_system.generate_feedback(match_result, cv_data, job_data)
    
    # Generate text report
    text_report = feedback_system.generate_report(feedback_report, format='text')
    print(text_report)
    
    # Generate HTML report
    html_report = feedback_system.generate_report(feedback_report, format='html')
    
    # Save HTML report to file
    with open('cv_match_report.html', 'w') as f:
        f.write(html_report)
