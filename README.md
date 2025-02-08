# ResRate
 A resume rater using gpt

Resume Rater
AI-Powered Resume Feedback Tool

Resume Rater is a web application that helps job seekers improve their resumes by providing AI-powered feedback. Users can upload their resumes (PDF format) and paste a job description to receive tailored suggestions on clarity, keyword alignment, and areas for improvement. Built with Flask, OpenAI GPT-4o, and Google OAuth, this tool is designed to be simple, secure, and user-friendly.

Features:

-Google OAuth Login: Securely log in with your Google account.
-PDF Resume Upload: Extract and analyze text from uploaded PDF resumes, that are NOT stored to ensure security.
-Job Description Analysis: Compare your resume against a job description to identify gaps and suggest improvements.
-AI-Powered Feedback: Leverage OpenAI’s GPT-4o for detailed, actionable feedback.
-Rate Limiting: Prevent abuse with a 5-requests-per-minute limit.

How It Works
-Log In: Sign in with your Google account.
-Upload Resume: Upload your resume in PDF format.
-Paste Job Description: Provide the job description you’re targeting.
-Get Feedback: Receive AI-generated feedback on your resume’s alignment with the job description.

Tech Stack
Backend: Flask (Python)
Frontend: HTML, Bootstrap
AI: OpenAI GPT-4o
Authentication: Google OAuth (Flask-Dance)
PDF Parsing: pdfplumber
Rate Limiting: Flask-Limiter


Setup Instructions

Clone the Repository:
BASH:

git clone https://github.com/your-username/resume-rater.git
cd resume-rater


Install Dependencies:
BASH:

pip install -r requirements.txt


Set Up Environment Variables:
Create a .env file in the root directory with the following:

SECRET_KEY="your_flask_secret_key_here"
OPENAI_API_KEY="sk-your-openai-api-key"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"


To run the App type: 
BASH:

python app.py

Hosted at http://localhost:5000


Future Enhancements
File Size Limit: Reject PDFs larger than 5MB.
Storage and memory: Implement SQL/noSQL storage to retain previous analysis and pdf version control.
Loading Spinner: Add a loading indicator during analysis.
Enhanced UI: Improve the design and user experience.
Error Handling: Provide better feedback for invalid inputs or API failures.

Contributing
Contributions are welcome! If you’d like to improve this project, please:

Fork the repository.

Create a new branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/your-feature).
And open a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
OpenAI for the GPT-4o API.
Flask and Flask-Dance for backend and authentication.
pdfplumber for PDF text extraction.