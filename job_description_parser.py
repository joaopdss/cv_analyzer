"""
Job Description Parser Module

This module extracts structured information from job descriptions using NLP techniques.
It identifies key requirements and preferences from job descriptions including:
- Required skills and technologies
- Experience requirements (years, roles, responsibilities)
- Education requirements
- Industry-specific qualifications
- Company culture indicators

The module is part of the CV-to-Job Matching System.
"""

import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import pandas as pd

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

# Common tech skills keywords
TECH_SKILLS = [
    'python', 'java', 'javascript', 'html', 'css', 'sql', 'nosql', 
    'react', 'angular', 'vue', 'node', 'express', 'django', 'flask',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'devops', 'ci/cd',
    'machine learning', 'deep learning', 'data science', 'ai', 
    'artificial intelligence', 'nlp', 'natural language processing',
    'computer vision', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau', 'power bi',
    'git', 'github', 'gitlab', 'bitbucket', 'agile', 'scrum', 'kanban',
    'rest api', 'graphql', 'microservices', 'serverless', 'linux', 'unix',
    'windows', 'macos', 'android', 'ios', 'swift', 'kotlin', 'flutter',
    'react native', 'c', 'c++', 'c#', '.net', 'ruby', 'rails', 'php',
    'laravel', 'symfony', 'wordpress', 'drupal', 'joomla', 'magento',
    'shopify', 'woocommerce', 'seo', 'sem', 'google analytics', 'adobe',
    'photoshop', 'illustrator', 'indesign', 'figma', 'sketch', 'xd',
    'ui/ux', 'user interface', 'user experience', 'responsive design',
    'mobile design', 'web design', 'graphic design', 'product design'
]

# Education terms
EDUCATION_TERMS = [
    'bachelor', 'master', 'phd', 'doctorate', 'degree', 'bs', 'ba', 'ms', 'ma',
    'mba', 'btech', 'mtech', 'b.e.', 'm.e.', 'b.tech', 'm.tech', 'diploma',
    'certification', 'certificate', 'graduate', 'undergraduate', 'postgraduate'
]

# Experience level indicators
EXPERIENCE_LEVELS = {
    'entry level': 0,
    'junior': 1,
    'mid-level': 3,
    'mid level': 3,
    'senior': 5,
    'lead': 7,
    'principal': 8,
    'staff': 6,
    'manager': 5,
    'director': 8,
    'head': 8,
    'chief': 10,
    'vp': 10,
    'executive': 10
}

class JobDescriptionParser:
    """
    A class for parsing job descriptions and extracting structured information.
    """
    
    def __init__(self, skills_file=None):
        """
        Initialize the Job Description Parser.
        
        Args:
            skills_file (str, optional): Path to CSV file containing skills list.
        """
        self.skills_file = skills_file
        self.skills_list = self._load_skills_list() if skills_file else TECH_SKILLS
    
    def _load_skills_list(self):
        """
        Load skills from CSV file.
        
        Returns:
            list: List of skills.
        """
        try:
            data = pd.read_csv(self.skills_file, names=['skill'])
            return data.skill.tolist()
        except Exception as e:
            print(f"Error loading skills file: {e}")
            return TECH_SKILLS
    
    def parse_job_description(self, text):
        """
        Parse job description and extract structured information.
        
        Args:
            text (str): Job description text.
            
        Returns:
            dict: Structured information extracted from job description.
        """
        # Process the text with spaCy
        doc = nlp(text)
        
        # Extract information
        result = {
            'required_skills': self._extract_skills(text),
            'experience_requirements': self._extract_experience(text),
            'education_requirements': self._extract_education(text),
            'job_title': self._extract_job_title(text),
            'job_type': self._extract_job_type(text),
            'location': self._extract_location(doc),
            'company_culture': self._extract_company_culture(text),
            'responsibilities': self._extract_responsibilities(text),
            'text': text  # Include the full text for reference
        }
        
        return result
    
    def _extract_skills(self, text):
        """
        Extract required skills from job description.
        
        Args:
            text (str): Job description text.
            
        Returns:
            list: List of required skills.
        """
        # Process the text with spaCy
        doc = nlp(text.lower())
        
        # Tokenize and remove stop words
        tokens = [token.text for token in doc if not token.is_stop]
        
        # Extract noun chunks as potential skills
        noun_chunks = list(doc.noun_chunks)
        
        # Identify sections likely to contain skills
        skills_section = self._find_section(text, ['skills', 'requirements', 'qualifications', 'what you need', 'what we require'])
        
        skillset = []
        
        # Check for skills in tokens (unigrams)
        for token in tokens:
            if token.lower() in [s.lower() for s in self.skills_list]:
                skillset.append(token)
        
        # Check for skills in noun chunks
        for chunk in noun_chunks:
            chunk_text = chunk.text.lower()
            if chunk_text in [s.lower() for s in self.skills_list]:
                skillset.append(chunk.text)
        
        # Generate bigrams and trigrams
        word_tokens = nltk.word_tokenize(text.lower())
        filtered_tokens = [w for w in word_tokens if w.isalpha() and w not in STOPWORDS]
        bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
        
        # Add bigrams and trigrams that might be skills
        for ngram in bigrams_trigrams:
            if ngram in [s.lower() for s in self.skills_list]:
                skillset.append(ngram)
        
        # Look for skills in the skills section if found
        if skills_section:
            for skill in self.skills_list:
                if skill.lower() in skills_section.lower():
                    skillset.append(skill)
        
        # Look for patterns like "Experience with X" or "Knowledge of X"
        experience_patterns = [
            r'experience (?:with|in|using) ([a-zA-Z0-9\+\#\-\.\s]+)',
            r'knowledge of ([a-zA-Z0-9\+\#\-\.\s]+)',
            r'proficient (?:with|in) ([a-zA-Z0-9\+\#\-\.\s]+)',
            r'familiarity with ([a-zA-Z0-9\+\#\-\.\s]+)',
            r'expertise in ([a-zA-Z0-9\+\#\-\.\s]+)'
        ]
        
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                potential_skill = match.group(1).strip()
                # Check if the potential skill contains any known skill
                for skill in self.skills_list:
                    if skill.lower() in potential_skill:
                        skillset.append(skill)
        
        # Remove duplicates and sort
        skillset = sorted(list(set([s.capitalize() for s in skillset])))
        
        return skillset
    
    def _extract_experience(self, text):
        """
        Extract experience requirements from job description.
        
        Args:
            text (str): Job description text.
            
        Returns:
            dict: Experience requirements including years and level.
        """
        experience = {
            'years': None,
            'level': None,
            'description': []
        }
        
        # Look for years of experience
        year_patterns = [
            r'(\d+)\+?\s*(?:years|yrs)(?:\s*of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years|yrs)',
            r'(\d+)\+?\s*(?:years|yrs)(?:\s*of)?\s*(?:relevant|related)?\s*experience',
            r'minimum\s*(?:of)?\s*(\d+)\+?\s*(?:years|yrs)'
        ]
        
        for pattern in year_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                years = int(match.group(1))
                if experience['years'] is None or years > experience['years']:
                    experience['years'] = years
        
        # Look for experience level
        for level, value in EXPERIENCE_LEVELS.items():
            if level in text.lower():
                if experience['level'] is None or value > EXPERIENCE_LEVELS.get(experience['level'], 0):
                    experience['level'] = level
        
        # Extract sentences that mention experience
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if 'experience' in sentence.lower():
                experience['description'].append(sentence.strip())
        
        return experience
    
    def _extract_education(self, text):
        """
        Extract education requirements from job description.
        
        Args:
            text (str): Job description text.
            
        Returns:
            list: Education requirements.
        """
        education = []
        
        # Find education section
        education_section = self._find_section(text, ['education', 'qualifications', 'requirements'])
        
        # If education section found, process it
        if education_section:
            # Look for education terms
            for term in EDUCATION_TERMS:
                if term in education_section.lower():
                    # Find the sentence containing the term
                    sentences = sent_tokenize(education_section)
                    for sentence in sentences:
                        if term in sentence.lower():
                            education.append(sentence.strip())
        
        # If no education section found or no terms found in section, search the entire text
        if not education:
            sentences = sent_tokenize(text)
            for sentence in sentences:
                if any(term in sentence.lower() for term in EDUCATION_TERMS):
                    education.append(sentence.strip())
        
        # Remove duplicates
        education = list(set(education))
        
        return education
    
    def _extract_job_title(self, text):
        """
        Extract job title from job description.
        
        Args:
            text (str): Job description text.
            
        Returns:
            str: Job title or None if not found.
        """
        # Look for common job title patterns
        title_patterns = [
            r'job title:?\s*([^\n\.]+)',
            r'position:?\s*([^\n\.]+)',
            r'role:?\s*([^\n\.]+)',
            r'we are looking for(?: an?| a)? ([^\n\.]+)',
            r'hiring(?: an?| a)? ([^\n\.]+)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, try to extract from first few sentences
        sentences = sent_tokenize(text)
        if sentences:
            first_sentence = sentences[0]
            # Look for job title in first sentence
            doc = nlp(first_sentence)
            for ent in doc.ents:
                if ent.label_ == 'WORK_OF_ART' or ent.label_ == 'ORG':
                    return ent.text
        
        return None
    
    def _extract_job_type(self, text):
        """
        Extract job type from job description.
        
        Args:
            text (str): Job description text.
            
        Returns:
            str: Job type or None if not found.
        """
        job_types = [
            'full-time', 'full time', 'part-time', 'part time', 'contract',
            'temporary', 'permanent', 'freelance', 'remote', 'hybrid', 'on-site',
            'on site', 'internship'
        ]
        
        text_lower = text.lower()
        found_types = []
        
        for job_type in job_types:
            if job_type in text_lower:
                found_types.append(job_type)
        
        if found_types:
            return ', '.join(found_types)
        
        return None
    
    def _extract_location(self, doc):
        """
        Extract job location from job description.
        
        Args:
            doc (spacy.Doc): Processed job description.
            
        Returns:
            str: Job location or None if not found.
        """
        # Look for location entities
        locations = []
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:
                locations.append(ent.text)
        
        if locations:
            return ', '.join(locations)
        
        # Look for location patterns
        location_patterns = [
            r'location:?\s*([^\n\.]+)',
            r'based in:?\s*([^\n\.]+)',
            r'position is (?:located|based) in:?\s*([^\n\.]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, doc.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_company_culture(self, text):
        """
        Extract company culture indicators from job description.
        
        Args:
            text (str): Job description text.
            
        Returns:
            list: Company culture indicators.
        """
        culture = []
        
        # Find company/culture section
        culture_section = self._find_section(text, ['company culture', 'about us', 'our culture', 'we offer', 'benefits', 'perks'])
        
        # Culture keywords to look for
        culture_keywords = [
            'flexible', 'work-life balance', 'work life balance', 'remote work',
            'diversity', 'inclusive', 'inclusion', 'growth', 'learning',
            'development', 'collaborative', 'team', 'innovative', 'creative',
            'fast-paced', 'fast paced', 'startup', 'enterprise', 'corporate',
            'casual', 'formal', 'relaxed', 'competitive', 'friendly', 'fun',
            'challenging', 'rewarding', 'transparent', 'open', 'communication',
            'feedback', 'mentorship', 'coaching', 'autonomy', 'independence',
            'responsibility', 'ownership', 'impact', 'mission', 'purpose',
            'values', 'ethics', 'social responsibility', 'sustainability',
            'environment', 'health', 'wellness', 'benefits', 'perks',
            'compensation', 'salary', 'bonus', 'equity', 'stock options'
        ]
        
        # If culture section found, process it
        if culture_section:
            sentences = sent_tokenize(culture_section)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in culture_keywords):
                    culture.append(sentence.strip())
        
        # If no culture section found or no keywords found in section, search the entire text
        if not culture:
            sentences = sent_tokenize(text)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in culture_keywords):
                    culture.append(sentence.strip())
        
        # Remove duplicates
        culture = list(set(culture))
        
        return culture
    
    def _extract_responsibilities(self, text):
        """
        Extract job responsibilities from job description.
        
        Args:
            text (str): Job description text.
            
        Returns:
            list: Job responsibilities.
        """
        responsibilities = []
        
        # Find responsibilities section
        resp_section = self._find_section(text, ['responsibilities', 'duties', 'what you\'ll do', 'job description', 'the role', 'day to day'])
        
        if resp_section:
            # Look for bullet points or numbered lists
            bullet_patterns = [
                r'•\s*([^\n•]+)',
                r'-\s*([^\n-]+)',
                r'\*\s*([^\n\*]+)',
                r'\d+\.\s*([^\n]+)'
            ]
            
            for pattern in bullet_patterns:
                matches = re.finditer(pattern, resp_section)
                for match in matches:
                    responsibilities.append(match.group(1).strip())
            
            # If no bullet points found, use sentences
            if not responsibilities:
                sentences = sent_tokenize(resp_section)
                for sentence in sentences:
                    # Skip short sentences and headers
                    if len(sentence) > 20 and not sentence.isupper():
                        responsibilities.append(sentence.strip())
        
        # If no responsibilities found, try to find sentences with action verbs
        if not responsibilities:
            action_verbs = [
                'develop', 'create', 'design', 'implement', 'manage', 'lead',
                'coordinate', 'analyze', 'build', 'maintain', 'support', 'test',
                'troubleshoot', 'resolve', 'improve', 'optimize', 'collaborate',
                'communicate', 'present', 'report', 'research', 'identify'
            ]
            
            sentences = sent_tokenize(text)
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                if any(verb in words for verb in action_verbs):
                    responsibilities.append(sentence.strip())
        
        return responsibilities
    
    def _find_section(self, text, section_headers):
        """
        Find a specific section in the job description.
        
        Args:
            text (str): Job description text.
            section_headers (list): Possible section headers to look for.
            
        Returns:
            str: Section text or None if not found.
        """
        # Try to find section headers with common formatting patterns
        for header in section_headers:
            # Look for headers with different formatting
            patterns = [
                rf'{header}:?\s*\n(.*?)(?:\n\n|\n[A-Z]|\Z)',  # Header followed by newline
                rf'{header}:?\s*(.*?)(?:\n\n|\n[A-Z]|\Z)',     # Header followed by text
                rf'\n{header}:?\s*\n(.*?)(?:\n\n|\n[A-Z]|\Z)', # Newline, header, newline
                rf'\*\*{header}\*\*:?\s*(.*?)(?:\n\n|\n[A-Z]|\Z)', # Markdown bold
                rf'#{header}#:?\s*(.*?)(?:\n\n|\n[A-Z]|\Z)'    # Markdown heading
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1).strip()
        
        return None

# Example usage
if __name__ == "__main__":
    # Create parser instance
    parser = JobDescriptionParser()
    
    # Example job description
    job_description = """
    Senior Python Developer
    
    About the Role:
    We are looking for a Senior Python Developer to join our team. This is a full-time position based in New York with hybrid work options.
    
    Responsibilities:
    • Design and implement high-quality Python code for our backend systems
    • Collaborate with cross-functional teams to define and implement new features
    • Optimize application performance and scalability
    • Write unit tests and integration tests
    • Mentor junior developers and conduct code reviews
    
    Requirements:
    • 5+ years of experience with Python development
    • Strong knowledge of Django or Flask frameworks
    • Experience with RESTful APIs and microservices architecture
    • Familiarity with AWS or other cloud platforms
    • Understanding of database systems (SQL and NoSQL)
    • Experience with version control systems (Git)
    • Bachelor's degree in Computer Science or related field
    
    Our Culture:
    We offer a collaborative and inclusive work environment where innovation is encouraged. We provide competitive compensation, health benefits, and opportunities for professional growth.
    """
    
    # Parse job description
    result = parser.parse_job_description(job_description)
    
    # Print results
    print("Extracted Information:")
    print(f"Job Title: {result['job_title']}")
    print(f"Job Type: {result['job_type']}")
    print(f"Location: {result['location']}")
    print(f"Required Skills: {', '.join(result['required_skills'])}")
    print(f"Experience: {result['experience_requirements']['years']} years, Level: {result['experience_requirements']['level']}")
    print(f"Education: {result['education_requirements']}")
    print(f"Responsibilities: {result['responsibilities'][:3]}...")  # Show first 3
    print(f"Company Culture: {result['company_culture'][:2]}...")  # Show first 2
