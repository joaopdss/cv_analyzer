"""
Matching Algorithm Module

This module compares CV data with job description data to calculate compatibility scores.
It uses semantic matching techniques to evaluate the similarity between different components
such as skills, experience, and education.

The module is part of the CV-to-Job Matching System.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
import re
import spacy
import math

# Download necessary NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    # If model not found, download it
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Initialize stopwords
STOPWORDS = set(stopwords.words('english'))

class MatchingAlgorithm:
    """
    A class for comparing CV data with job description data to calculate compatibility scores.
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the Matching Algorithm.
        
        Args:
            model_name (str, optional): Name of the sentence-transformers model to use.
        """
        # Load sentence transformer model for semantic matching
        try:
            self.model = SentenceTransformer(model_name)
        except:
            # If model not found, download it
            import subprocess
            subprocess.run(['pip', 'install', 'sentence-transformers'])
            self.model = SentenceTransformer(model_name)
        
        # Define component weights for overall score calculation
        self.weights = {
            'skills': 0.35,
            'experience': 0.30,
            'education': 0.20,
            'overall': 0.15
        }
    
    def calculate_match(self, cv_data, job_data):
        """
        Calculate the match score between CV and job description.
        
        Args:
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            dict: Match scores for different components and overall match percentage.
        """
        # Calculate individual component scores
        skills_score = self._match_skills(cv_data.get('skills', []), job_data.get('required_skills', []))
        experience_score = self._match_experience(cv_data, job_data)
        education_score = self._match_education(cv_data.get('education', []), job_data.get('education_requirements', []))
        
        # Calculate semantic similarity between full CV text and job description
        overall_score = self._calculate_semantic_similarity(cv_data.get('text', ''), job_data.get('text', ''))
        
        # Calculate weighted average for final score
        final_score = (
            self.weights['skills'] * skills_score +
            self.weights['experience'] * experience_score +
            self.weights['education'] * education_score +
            self.weights['overall'] * overall_score
        )
        
        # Prepare detailed match report
        match_report = {
            'overall_match': round(final_score * 100, 2),
            'components': {
                'skills': {
                    'score': round(skills_score * 100, 2),
                    'weight': self.weights['skills'],
                    'matched': self._get_matched_skills(cv_data.get('skills', []), job_data.get('required_skills', [])),
                    'missing': self._get_missing_skills(cv_data.get('skills', []), job_data.get('required_skills', []))
                },
                'experience': {
                    'score': round(experience_score * 100, 2),
                    'weight': self.weights['experience'],
                    'details': self._get_experience_details(cv_data, job_data)
                },
                'education': {
                    'score': round(education_score * 100, 2),
                    'weight': self.weights['education'],
                    'details': self._get_education_details(cv_data.get('education', []), job_data.get('education_requirements', []))
                },
                'overall_similarity': {
                    'score': round(overall_score * 100, 2),
                    'weight': self.weights['overall']
                }
            }
        }
        
        return match_report
    
    def _match_skills(self, cv_skills, job_skills):
        """
        Match skills from CV with required skills from job description.
        
        Args:
            cv_skills (list): Skills extracted from CV.
            job_skills (list): Required skills from job description.
            
        Returns:
            float: Skills match score between 0 and 1.
        """
        if not job_skills:
            return 1.0  # If no skills required, perfect match
        
        if not cv_skills:
            return 0.0  # If no skills in CV but skills required, no match
        
        # Convert to lowercase for case-insensitive matching
        cv_skills_lower = [skill.lower() for skill in cv_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Calculate exact matches
        exact_matches = sum(1 for skill in job_skills_lower if skill in cv_skills_lower)
        
        # Calculate semantic matches for skills that didn't match exactly
        semantic_score = 0
        remaining_job_skills = [skill for skill in job_skills_lower if skill not in cv_skills_lower]
        
        if remaining_job_skills and cv_skills:
            # Encode all skills
            cv_embeddings = self.model.encode(cv_skills_lower)
            job_embeddings = self.model.encode(remaining_job_skills)
            
            # Calculate cosine similarity between each pair
            similarity_matrix = cosine_similarity(job_embeddings, cv_embeddings)
            
            # For each remaining job skill, find the best matching CV skill
            for i in range(len(remaining_job_skills)):
                best_match = np.max(similarity_matrix[i])
                if best_match > 0.75:  # Threshold for considering a semantic match
                    semantic_score += best_match
        
        # Calculate final score as a weighted combination of exact and semantic matches
        total_required_skills = len(job_skills)
        exact_match_weight = 0.7
        semantic_match_weight = 0.3
        
        score = (exact_match_weight * exact_matches + semantic_match_weight * semantic_score) / total_required_skills
        
        # Cap the score at 1.0
        return min(score, 1.0)
    
    def _match_experience(self, cv_data, job_data):
        """
        Match experience from CV with required experience from job description.
        
        Args:
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            float: Experience match score between 0 and 1.
        """
        # Extract experience requirements from job description
        job_experience = job_data.get('experience_requirements', {})
        required_years = job_experience.get('years')
        
        # If no specific experience requirement, consider it a match
        if not required_years:
            return 1.0
        
        # Try to extract years of experience from CV
        cv_experience_years = self._extract_experience_years(cv_data)
        
        # Calculate years match score
        years_score = 0.0
        if cv_experience_years is not None:
            if cv_experience_years >= required_years:
                years_score = 1.0
            else:
                # Partial credit for experience close to required
                years_score = cv_experience_years / required_years
        
        # Calculate relevance score by comparing experience descriptions
        relevance_score = 0.0
        cv_experience_text = ' '.join(cv_data.get('text', '').split())  # Full CV text as fallback
        job_responsibilities = ' '.join(job_data.get('responsibilities', []))
        
        if cv_experience_text and job_responsibilities:
            relevance_score = self._calculate_semantic_similarity(cv_experience_text, job_responsibilities)
        
        # Combine scores with weights
        years_weight = 0.6
        relevance_weight = 0.4
        
        return years_weight * years_score + relevance_weight * relevance_score
    
    def _match_education(self, cv_education, job_education_requirements):
        """
        Match education from CV with required education from job description.
        
        Args:
            cv_education (list): Education information extracted from CV.
            job_education_requirements (list): Required education from job description.
            
        Returns:
            float: Education match score between 0 and 1.
        """
        # If no education requirements specified, consider it a match
        if not job_education_requirements:
            return 1.0
        
        # If no education in CV but education required, low match
        if not cv_education:
            return 0.2  # Small baseline score
        
        # Combine all education text
        cv_education_text = ' '.join(cv_education)
        job_education_text = ' '.join(job_education_requirements)
        
        # Calculate semantic similarity between education texts
        education_similarity = self._calculate_semantic_similarity(cv_education_text, job_education_text)
        
        # Check for degree level matches
        degree_levels = {
            'bachelor': 1,
            'bs': 1,
            'ba': 1,
            'undergraduate': 1,
            'master': 2,
            'ms': 2,
            'ma': 2,
            'mba': 2,
            'graduate': 2,
            'phd': 3,
            'doctorate': 3,
            'doctoral': 3,
            'postgraduate': 3
        }
        
        # Extract highest degree level from CV and job requirements
        cv_degree_level = 0
        job_degree_level = 0
        
        for level, value in degree_levels.items():
            if level in cv_education_text.lower():
                cv_degree_level = max(cv_degree_level, value)
            if level in job_education_text.lower():
                job_degree_level = max(job_degree_level, value)
        
        # Calculate degree level match
        degree_match = 0.0
        if job_degree_level > 0:
            if cv_degree_level >= job_degree_level:
                degree_match = 1.0
            else:
                # Partial credit for being close
                degree_match = cv_degree_level / job_degree_level
        else:
            # If no specific degree level mentioned in job, consider it a match
            degree_match = 1.0
        
        # Combine semantic similarity and degree level match
        similarity_weight = 0.5
        degree_weight = 0.5
        
        return similarity_weight * education_similarity + degree_weight * degree_match
    
    def _calculate_semantic_similarity(self, text1, text2):
        """
        Calculate semantic similarity between two texts using sentence embeddings.
        
        Args:
            text1 (str): First text.
            text2 (str): Second text.
            
        Returns:
            float: Semantic similarity score between 0 and 1.
        """
        if not text1 or not text2:
            return 0.0
        
        # Encode texts
        embedding1 = self.model.encode(text1)
        embedding2 = self.model.encode(text2)
        
        # Calculate cosine similarity
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        
        # Normalize to [0, 1] range
        return max(0.0, min(similarity, 1.0))
    
    def _extract_experience_years(self, cv_data):
        """
        Extract years of experience from CV data.
        
        Args:
            cv_data (dict): Structured data extracted from CV.
            
        Returns:
            int or None: Years of experience or None if not found.
        """
        # Try to find years of experience in the CV text
        cv_text = cv_data.get('text', '')
        
        # Look for patterns like "X years of experience"
        year_patterns = [
            r'(\d+)\+?\s*(?:years|yrs)(?:\s*of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years|yrs)',
            r'(\d+)\+?\s*(?:years|yrs)(?:\s*of)?\s*(?:relevant|related)?\s*experience',
            r'(?:over|more than)\s*(\d+)\s*(?:years|yrs)'
        ]
        
        max_years = None
        for pattern in year_patterns:
            matches = re.finditer(pattern, cv_text.lower())
            for match in matches:
                years = int(match.group(1))
                if max_years is None or years > max_years:
                    max_years = years
        
        return max_years
    
    def _get_matched_skills(self, cv_skills, job_skills):
        """
        Get list of skills that match between CV and job requirements.
        
        Args:
            cv_skills (list): Skills extracted from CV.
            job_skills (list): Required skills from job description.
            
        Returns:
            list: Matched skills.
        """
        if not cv_skills or not job_skills:
            return []
        
        # Convert to lowercase for case-insensitive matching
        cv_skills_lower = [skill.lower() for skill in cv_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Find exact matches
        exact_matches = [skill for skill in job_skills if skill.lower() in cv_skills_lower]
        
        # Find semantic matches for skills that didn't match exactly
        semantic_matches = []
        remaining_job_skills = [skill for skill in job_skills if skill.lower() not in cv_skills_lower]
        
        if remaining_job_skills and cv_skills:
            # Encode all skills
            cv_embeddings = self.model.encode([skill.lower() for skill in cv_skills])
            job_embeddings = self.model.encode([skill.lower() for skill in remaining_job_skills])
            
            # Calculate cosine similarity between each pair
            similarity_matrix = cosine_similarity(job_embeddings, cv_embeddings)
            
            # For each remaining job skill, find the best matching CV skill
            for i, job_skill in enumerate(remaining_job_skills):
                best_match_index = np.argmax(similarity_matrix[i])
                best_match_score = similarity_matrix[i][best_match_index]
                
                if best_match_score > 0.75:  # Threshold for considering a semantic match
                    semantic_matches.append({
                        'job_skill': job_skill,
                        'cv_skill': cv_skills[best_match_index],
                        'similarity': round(best_match_score, 2)
                    })
        
        return {
            'exact': exact_matches,
            'semantic': semantic_matches
        }
    
    def _get_missing_skills(self, cv_skills, job_skills):
        """
        Get list of required skills that are missing from the CV.
        
        Args:
            cv_skills (list): Skills extracted from CV.
            job_skills (list): Required skills from job description.
            
        Returns:
            list: Missing skills.
        """
        if not job_skills:
            return []
        
        if not cv_skills:
            return job_skills
        
        # Convert to lowercase for case-insensitive matching
        cv_skills_lower = [skill.lower() for skill in cv_skills]
        
        # Find exact misses
        exact_misses = [skill for skill in job_skills if skill.lower() not in cv_skills_lower]
        
        # Remove semantic matches from misses
        semantic_matches = self._get_matched_skills(cv_skills, job_skills).get('semantic', [])
        semantic_match_job_skills = [match['job_skill'] for match in semantic_matches]
        
        missing_skills = [skill for skill in exact_misses if skill not in semantic_match_job_skills]
        
        return missing_skills
    
    def _get_experience_details(self, cv_data, job_data):
        """
        Get detailed comparison of experience between CV and job requirements.
        
        Args:
            cv_data (dict): Structured data extracted from CV.
            job_data (dict): Structured data extracted from job description.
            
        Returns:
            dict: Experience comparison details.
        """
        # Extract experience requirements from job description
        job_experience = job_data.get('experience_requirements', {})
        required_years = job_experience.get('years')
        required_level = job_experience.get('level')
        
        # Extract experience from CV
        cv_experience_years = self._extract_experience_years(cv_data)
        
        details = {
            'required_years': required_years,
            'cv_years': cv_experience_years,
            'required_level': required_level,
            'gap': None
        }
        
        # Calculate gap
        if required_years is not None and cv_experience_years is not None:
            details['gap'] = required_years - cv_experience_years
        
        return details
    
    def _get_education_details(self, cv_education, job_education_requirements):
        """
        Get detailed comparison of education between CV and job requirements.
        
        Args:
            cv_education (list): Education information extracted from CV.
            job_education_requirements (list): Required education from job description.
            
        Returns:
            dict: Education comparison details.
        """
        # Combine all education text
        cv_education_text = ' '.join(cv_education) if cv_education else ''
        job_education_text = ' '.join(job_education_requirements) if job_education_requirements else ''
        
        # Define degree levels
        degree_levels = {
            'bachelor': 1,
            'bs': 1,
            'ba': 1,
            'undergraduate': 1,
            'master': 2,
            'ms': 2,
            'ma': 2,
            'mba': 2,
            'graduate': 2,
            'phd': 3,
            'doctorate': 3,
            'doctoral': 3,
            'postgraduate': 3
        }
        
        # Extract highest degree level from CV and job requirements
        cv_degree_level = 0
        cv_degree_name = None
        job_degree_level = 0
        job_degree_name = None
        
        for level, value in degree_levels.items():
            if level in cv_education_text.lower():
                if value > cv_degree_level:
                    cv_degree_level = value
                    cv_degree_name = level
            if level in job_education_text.lower():
                if value > job_degree_level:
                    job_degree_level = value
                    job_degree_name = level
        
        details = {
            'cv_degree_level': cv_degree_name,
            'required_degree_level': job_degree_name,
            'meets_requirements': cv_degree_level >= job_degree_level if job_degree_level > 0 else True
        }
        
        return details

# Example usage
if __name__ == "__main__":
    # Create matching algorithm instance
    matcher = MatchingAlgorithm()
    
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
    
    # Calculate match
    match_result = matcher.calculate_match(cv_data, job_data)
    
    # Print results
    print(f"Overall Match: {match_result['overall_match']}%")
    print("\nComponent Scores:")
    for component, details in match_result['components'].items():
        print(f"- {component}: {details['score']}%")
    
    print("\nMatched Skills:")
    for skill in match_result['components']['skills']['matched']['exact']:
        print(f"- {skill} (exact match)")
    for match in match_result['components']['skills']['matched']['semantic']:
        print(f"- {match['job_skill']} (similar to {match['cv_skill']}, similarity: {match['similarity']})")
    
    print("\nMissing Skills:")
    for skill in match_result['components']['skills']['missing']:
        print(f"- {skill}")
