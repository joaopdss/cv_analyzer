# CV-to-Job Matching System - User Guide

This guide provides instructions for accessing and using the deployed CV-to-Job Matching System.

## Accessing the Website

Once deployed, the CV-to-Job Matching System will be available at:

```
https://cv-job-matching.onrender.com
```

(Replace "cv-job-matching" with the actual name you chose during deployment)

## Using the System

### Analyzing a CV Against a Job Description

1. **Access the Website**: Navigate to the URL of your deployed application
2. **Upload Your CV**: Click the "Choose File" button and select your CV (supported formats: PDF, DOCX, DOC, TXT)
3. **Enter Job Description**: Paste the complete job description in the text area
4. **Analyze**: Click the "Analyze Match" button
5. **View Results**: After processing, you'll see:
   - Overall match percentage
   - Detailed feedback on skills, experience, and education
   - Recommendations for improving your CV
   - Option to view a detailed report

### Viewing Detailed Reports

1. After analysis, click the "View Detailed Report" button
2. The report opens in a new tab with comprehensive information about your match
3. You can save or print this report for future reference

### Using the API

For programmatic access, you can use the API endpoint:

```python
import requests

url = 'https://cv-job-matching.onrender.com/api/analyze'
files = {'cv_file': open('your_cv.pdf', 'rb')}
data = {'job_description': 'Job description text...'}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Match Percentage: {result['match_percentage']}%")
print(f"Feedback: {result['feedback']}")
```

## Tips for Best Results

1. **CV Format**: Ensure your CV is well-structured with clear sections for skills, experience, and education
2. **Complete Job Descriptions**: Include the full job description for more accurate matching
3. **File Size**: Keep CV files under 16MB for optimal processing
4. **Multiple Analyses**: Try analyzing your CV against different job descriptions to see how your match varies

## Troubleshooting

If you encounter issues:

1. **File Format Errors**: Ensure your CV is in one of the supported formats (PDF, DOCX, DOC, TXT)
2. **Processing Errors**: If analysis fails, try with a simpler CV format or a different file
3. **Slow Response**: For large files, the analysis may take longer to complete
4. **Connection Issues**: If the website is unresponsive, try again later as free-tier services may have periodic maintenance

## Privacy Considerations

- CV data is processed securely and not shared with third parties
- Analysis results are stored temporarily for performance reasons
- No personal data is retained long-term unless explicitly configured

## Getting Help

If you need assistance with the CV-to-Job Matching System:

1. Check the documentation in the GitHub repository
2. Review the troubleshooting section above
3. Contact the system administrator for specific deployment issues
