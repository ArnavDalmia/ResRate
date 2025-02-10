from flask import Flask, render_template, request, session, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
import os
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Load environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Google OAuth Setup
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ],
    redirect_to="index"  # Redirect to the 'index' route after login
)
app.register_blueprint(google_bp, url_prefix="/login")

# Rate Limiting (5 requests/minute)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"],
    storage_uri="memory://"
)

# PDF Processing
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

# Routes
@app.route('/')
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Fetch user info
    resp = google.get("/userinfo")
    if not resp.ok:
        user_info = {"name": "Guest"}  # Default fallback
    else:
        user_info = resp.json()

    return render_template('index.html', user=user_info)


#{{ google.get("/oauth2/v2/userinfo").json()["name"] }}

@app.route('/analyze', methods=['POST'])
@limiter.limit("5/minute")
def analyze():
    if 'resume' not in request.files:
        return "No resume provided", 400

    file = request.files['resume']
    if not file or not allowed_file(file.filename):
        return "Invalid file type. Only PDFs are allowed.", 400

    # Process PDF
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    resume_text = extract_text_from_pdf(filepath)
    os.remove(filepath)  # Cleanup after processing

    # Get Job Description
    job_desc = request.form.get('job_desc', '')

    # Get Additional Comments
    comments = request.form.get('comments', '')

    # GPT-4o Analysis
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
Analyze this resume for clarity, alignment with the provided job description, and overall effectiveness. Take into account use the additional information that is provided in the comments if they are related to the resume critique. If the comments are not related then keep the resume stuff seperate but in the end of the analysis address the comment. Provide detailed, actionable feedback:


Check if its a resume first of all. If its not a resume say Im not sure what to do with this.
---
**Minimal Changes IDEA**  
- Suggestions should be minimal and critical rather than things that could be open to subjectivity. If the resume is relatively strong, limit suggestions to minor improvements. Use the guage if they are a junior, intermiedate, and senior and the job desc to make this decision. If they are one of those people who have a strong resume just give a few holistic points and scrap the rest of the analysis.

**1. Initial Impression**  
- Start with a blunt, honest assessment of the user’s level and experience. For example:  
  - "I believe you are a junior student with limited professional experience."  
  - "Your resume suggests you are an intermediate candidate with strong technical skills."  
  - "Your resume lacks focus and seems to showcase everything rather than a specialization in a specific field."  

---

**2. Clarity and Structure**  
- Highlight vague or unclear sections. For example:  
  - "This bullet point is unclear: 'Worked on a team project.' Specify your role, tools used, and outcomes."  
- Check if points follow the **XYZ** or **STAR** method:  
  - "This point could be improved using the XYZ method: 'Increased sales by 20% (X) by implementing a new CRM system (Y), resulting in $50K in additional revenue (Z).'"  
- Suggest rewrites for poorly structured points, explaining what the current phrasing communicates versus what should be communicated.  

---

**3. Alignment with Job Description**  
- If a job description is provided:  
  - Identify **missing keywords or skills** (especially in the technical skills section) that are critical for ATS scanners.  
  - Suggest **concrete improvements** (e.g., metrics, achievements) if the resume lacks depth in required areas.  
  - If the job description is too advanced for the user’s level, explicitly state this:  
    - "This job description is for a senior-level role. Based on your resume, you may not yet meet the required experience."  
  - If the job description demands a specific GPA:  
    - If the user’s GPA matches: Do not mention it.  
    - If the user’s GPA is missing: "Add your GPA, as it is required by the job description."  
    - If the user’s GPA does not match: "Remove your GPA, as it does not meet the job description’s requirement."  

- If no job description is provided:  
  - Use the resume to gauge the user’s field and level (junior, intermediate, advanced).  
  - Provide general advice tailored to their inferred level and field.  

---

**4. Technical Skills and Projects**  
- Evaluate the **technical skills section**:  
  - If skills are slightly mentioned but not emphasized, suggest expanding on them to improve ATS compatibility.  
  - If the user is a junior, suggest adding foundational skills (e.g., Python, Git, SQL).  
  - If the user is intermediate/advanced, suggest advanced skills or certifications relevant to their field.  
- Review **projects** (professional or academic):  
  - If projects are irrelevant to the job description or field, suggest removing or modifying them.  
  - If projects lack detail, suggest adding metrics, tools used, and outcomes.  

---

**5. Learning Recommendations**  
- Based on the job description or inferred field, suggest **specific skills or tools** to learn. For example:  
  - "Consider learning Docker and Kubernetes, as they are frequently mentioned in DevOps job descriptions."  
  - "If you’re targeting data science roles, learn Pandas and Scikit-learn."  

---

**6. Professional Tone and Focus**  
- Ensure feedback is adapted to the user’s profession. For example:  
  - For software engineers: Focus on technical skills, projects, and tools.  
  - For business roles: Focus on leadership, metrics, and impact.  
- If the resume lacks focus:  
  - "Your resume seems to showcase everything rather than a specialization. Tailor it to the specific field or role you’re targeting."  

---
**7. Final Advice**  
- Summarize the most critical changes needed.  
- Encourage the user to focus on their strengths and tailor their resume to their target roles.  

---

**Example Output**  
**1. Initial Impression**  
"I believe you are a junior student with limited professional experience. Your resume shows potential but lacks focus and depth in key areas."  

**2. Clarity and Structure**  
- "This bullet point is unclear: 'Worked on a team project.' Specify your role, tools used, and outcomes."  
- "This point could be improved using the XYZ method: 'Increased sales by 20% (X) by implementing a new CRM system (Y), resulting in $50K in additional revenue (Z).'"  

**3. Alignment with Job Description**  
- "Missing keywords: Add 'Python' and 'AWS' to your technical skills section, as they are required by the job description."  
- "This job description is for a senior-level role. Based on your resume, you may not yet meet the required experience."  

**4. Technical Skills and Projects**  
- "Consider adding foundational skills like Git and SQL to your technical skills section."  
- "Your project 'Weather App' is irrelevant to the job description. Either remove it or modify it to highlight relevant skills."  

**5. Learning Recommendations**  
- "Consider learning Docker and Kubernetes, as they are frequently mentioned in DevOps job descriptions."  

**6. Professional Tone and Focus**  
- "Your resume seems to showcase everything rather than a specialization. Tailor it to the specific field or role you’re targeting."  

**7. Final Advice**  
- "Focus on adding metrics to quantify your achievements and tailor your resume to your target roles."  


---
    RESUME: {resume_text[:3000]}
    JOB DESCRIPTION: {job_desc[:1000]}
    COMMENTS: {comments[:1000]}
    """

    response = client.chat.completions.create(
        model="o1-mini", #gpt-4o
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return render_template('analyze.html', analysis=response.choices[0].message.content)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)