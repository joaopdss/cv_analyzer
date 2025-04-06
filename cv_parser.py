"""
CV Parser Module

This module extracts structured information from CV documents in various formats (PDF, DOCX, TXT).
It uses NLP techniques to identify and extract key information such as:
- Personal information
- Skills and technologies
- Work experience
- Education
- Certifications

The module is part of the CV-to-Job Matching System.
"""

import os
import re
import pandas as pd
import spacy
import nltk
from nltk.corpus import stopwords
import docx2txt
from pdfminer.high_level import extract_text

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

# Education degrees for education extraction
EDUCATION = [
    'BE', 'B.E.', 'B.E', 'BS', 'B.S', 'B.S.',
    'ME', 'M.E', 'M.E.', 'M.B.A', 'MBA', 'MS', 'M.S',
    'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
    'SSLC', 'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII',
    'PHD', 'PH.D', 'PH.D.', 'DOCTORATE',
    'BACHELOR', 'MASTERS', 'MASTER', 'DIPLOMA'
]

class CVParser:
    """
    A class for parsing CV documents and extracting structured information.
    """
    
    def __init__(self, skills_file=None):
        """
        Initialize the CV Parser.
        
        Args:
            skills_file (str, optional): Path to CSV file containing skills list.
        """
        self.skills_file = skills_file
        self.skills_list = self._load_skills_list() if skills_file else []
    
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
            return []
    
    def parse_cv(self, file_path):
        """
        Parse CV document and extract structured information.
        
        Args:
            file_path (str): Path to CV document.
            
        Returns:
            dict: Structured information extracted from CV.
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text based on file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            text = self._extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            text = self._extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Extract information
        result = {
            'email': self._extract_email(text),
            'phone': self._extract_phone_number(text),
            'skills': self._extract_skills(text),
            'education': self._extract_education(text),
            'name': self._extract_name(text),
            'text': text  # Include the full text for reference
        }
        
        return result
    
    def _extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF file.
        
        Args:
            pdf_path (str): Path to PDF file.
            
        Returns:
            str: Extracted text.
        """
        try:
            return extract_text(pdf_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def _extract_text_from_docx(self, docx_path):
        """
        Extract text from DOCX file.
        
        Args:
            docx_path (str): Path to DOCX file.
            
        Returns:
            str: Extracted text.
        """
        try:
            txt = docx2txt.process(docx_path)
            if txt:
                return txt.replace('\t', ' ')
            return ""
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def _extract_email(self, text):
        """
        Extract email address from text.
        
        Args:
            text (str): Text to extract email from.
            
        Returns:
            str: Extracted email address or None if not found.
        """
        email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = re.findall(email_regex, text)
        return emails[0] if emails else None
    
    def _extract_phone_number(self, text):
        """
        Extract phone number from text.
        
        Args:
            text (str): Text to extract phone number from.
            
        Returns:
            str: Extracted phone number or None if not found.
        """
        phone_regex = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
        phone = re.findall(phone_regex, text)
        
        if phone:
            number = ''.join(phone[0])
            if text.find(number) >= 0 and len(number) < 16:
                return number
        return None
    
    def _extract_name(self, text):
        """
        Extract name from text using spaCy NER.
        
        Args:
            text (str): Text to extract name from.
            
        Returns:
            str: Extracted name or None if not found.
        """
        # Use first 500 characters for name extraction (usually at the top of CV)
        doc = nlp(text[:500])
        
        # Look for PERSON entities
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
        
        return None
    
    def _extract_skills(self, text):
        """
        Extract skills from text.
        
        Args:
            text (str): Text to extract skills from.
            
        Returns:
            list: List of extracted skills.
        """
        # Process the text with spaCy
        doc = nlp(text.lower())
        
        # Tokenize and remove stop words
        tokens = [token.text for token in doc if not token.is_stop]
        
        # Extract noun chunks as potential skills
        noun_chunks = list(doc.noun_chunks)
        
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
        
        # If no skills list is provided, use a more general approach
        if not self.skills_list:
            # Generate bigrams and trigrams
            word_tokens = nltk.word_tokenize(text.lower())
            filtered_tokens = [w for w in word_tokens if w.isalpha() and w not in STOPWORDS]
            bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
            
            # Common tech skills keywords
            tech_keywords = ['python', 'java', 'javascript', 'html', 'css', 'sql', 'nosql', 
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
                            'mobile design', 'web design', 'graphic design', 'product design']
            
            # Add common tech skills found in the text
            for keyword in tech_keywords:
                if keyword in text.lower():
                    skillset.append(keyword)
            
            # Add bigrams and trigrams that might be skills
            for ngram in bigrams_trigrams:
                if ngram in text.lower() and ngram in tech_keywords:
                    skillset.append(ngram)
        
        # Remove duplicates and sort
        skillset = sorted(list(set([s.capitalize() for s in skillset])))
        
        return skillset
    
    def _extract_education(self, text):
        """
        Extract education information from text.
        
        Args:
            text (str): Text to extract education from.
            
        Returns:
            list: List of extracted education qualifications.
        """
        # Process the text with NLTK
        sentences = nltk.sent_tokenize(text)
        
        # Initialize education dictionary
        education = {}
        
        # Extract education degree
        for index, sentence in enumerate(sentences):
            for tex in sentence.split():
                # Replace special symbols
                tex = re.sub(r'[^\w\s]', ' ', tex)
                
                if tex.upper() in EDUCATION and tex not in STOPWORDS:
                    education[tex] = text[index:index+1]
        
        # If no education found using the above method, try a more general approach
        if not education:
            # Look for education-related keywords
            edu_keywords = ['degree', 'university', 'college', 'school', 'institute', 
                           'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certification']
            
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in edu_keywords):
                    # Add the sentence as potential education information
                    education[sentence[:20] + '...'] = sentence
        
        return list(education.values())

# Example usage
if __name__ == "__main__":
    # Create parser instance
    parser = CVParser()
    
    # Example file path (replace with actual path)
    file_path = "example_cv.pdf"
    
    try:
        # Parse CV
        result = parser.parse_cv(file_path)
        
        # Print results
        print("Extracted Information:")
        print(f"Name: {result['name']}")
        print(f"Email: {result['email']}")
        print(f"Phone: {result['phone']}")
        print(f"Skills: {', '.join(result['skills'])}")
        print(f"Education: {result['education']}")
    except Exception as e:
        print(f"Error parsing CV: {e}")
