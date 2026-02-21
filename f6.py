import streamlit as st
import random

# ================== Config ==================
heading_format = {
    "CONTACT": ["CONTACT", "CONTACT INFO", "CONTACT INFORMATION", "PHONE", "EMAIL"],
    "PROFILE": ["PROFILE", "CAREER OBJECTIVE", "SUMMARY", "ABOUT ME"],
    "SKILLS": ["SKILLS", "TECHNICAL SKILLS", "CORE SKILLS"],
    "LANGUAGES": ["LANGUAGES", "LANGUAGE PROFICIENCY"],
    "HOBBIES": ["HOBBIES", "INTERESTS", "EXTRA-CURRICULAR"],
    "PROFESSIONAL EXPERIENCE": ["PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE", "EXPERIENCE", "PROJECTS"],
    "EDUCATION": ["EDUCATION", "ACADEMICS", "QUALIFICATIONS", "DEGREES"]
}

core_tech = ["embedded c", "vlsi", "pcb design", "networking", "plc", "matlab"]
core_soft = ["communication", "problem solving", "teamwork", "leadership", "adaptability"]

# Sample ENTC jobs
jobs_list = [
    {"post": "Embedded Engineer", "salary": "₹5,00,000/yr"},
    {"post": "VLSI Designer", "salary": "₹6,00,000/yr"},
    {"post": "Network Engineer", "salary": "₹4,50,000/yr"},
    {"post": "PLC Programmer", "salary": "₹5,50,000/yr"}
]

# ================== Functions ==================
def check_resume_pattern(resume_text):
    resume_text = resume_text.upper()
    matched, missing = [], []
    for heading, variations in heading_format.items():
        if any(var in resume_text for var in variations):
            matched.append(heading)
        else:
            missing.append(heading)
    score = round((len(matched)/len(heading_format))*100, 2)
    eligible = score >= 60
    return score, eligible, matched, missing

def evaluate_profile(name, marks, tech_skills, soft_skills):
    matched_tech = [s for s in tech_skills if s.lower() in core_tech]
    matched_soft = [s for s in soft_skills if s.lower() in core_soft]

    tech_score = len(matched_tech) * 10
    soft_score = len(matched_soft) * 10
    total_score = round((tech_score + soft_score + marks)/3, 2)

    status = "Shortlisted" if total_score >= 60 else "Rejected"
    rank = random.randint(1,50) if status == "Shortlisted" else None

    # Suggest jobs only if eligible
    suggested_jobs = []
    if status == "Shortlisted":
        for job in jobs_list:
            suggested_jobs.append(job)

    return {
        "name": name,
        "total_score": total_score,
        "matched_tech": matched_tech,
        "matched_soft": matched_soft,
        "status": status,
        "rank": rank,
        "suggested_jobs": suggested_jobs
    }

# ================== Streamlit App ==================
st.title("AI Resume & Hiring System")

# ---------------- Step 1: Resume Upload ----------------
st.header("Step 1: Resume Pattern Checker")
resume_file = st.file_uploader("Upload your resume (PDF or TXT)", type=['pdf','txt'])

resume_eligible = False
resume_text = ""

if resume_file is not None:
    try:
        if resume_file.type == "application/pdf":
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(resume_file)
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text() + " "
            except ImportError:
                st.error("PyPDF2 not installed. Run `pip install PyPDF2`.")
        else:
            resume_text = resume_file.read().decode("utf-8")

        score, resume_eligible, matched, missing = check_resume_pattern(resume_text)
        st.write(f"**Resume Score:** {score}%")
        st.write(f"**Matched Sections:** {matched}")
        st.write(f"**Missing Sections:** {missing}")

        if resume_eligible:
            st.success("✅ Resume eligible for next step (≥ 60%)")
        else:
            st.error("❌ Resume not eligible (must match at least 60% of required sections)")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# ---------------- Step 2: Profile Evaluation ----------------
if resume_eligible:
    st.header("Step 2: Job Eligibility")
    with st.form("profile_form"):
        name = st.text_input("Name")
        marks = st.number_input("Aggregate Marks (%)", min_value=0, max_value=100, value=70)
        tech_input = st.text_input("Technical Skills (comma-separated)", "embedded c, vlsi")
        soft_input = st.text_input("Soft Skills (comma-separated)", "communication, teamwork")
        submitted = st.form_submit_button("Evaluate Profile")

    if submitted:
        tech_skills = [s.strip() for s in tech_input.split(",")]
        soft_skills = [s.strip() for s in soft_input.split(",")]

        result = evaluate_profile(name, marks, tech_skills, soft_skills)

        st.write(f"**Candidate Name:** {result['name']}")
        st.write(f"**Total Score:** {result['total_score']}")
        st.write(f"**Status:** {result['status']}")
        st.write(f"**Matched Technical Skills:** {', '.join(result['matched_tech']) if result['matched_tech'] else 'None'}")
        st.write(f"**Matched Soft Skills:** {', '.join(result['matched_soft']) if result['matched_soft'] else 'None'}")
        st.write(f"**Rank:** {result['rank'] if result['rank'] else 'N/A'}")

        # ---------------- Step 3: Job Suggestions ----------------
        if result['status'] == "Shortlisted":
            st.subheader("Job Suggestions")
            for job in result['suggested_jobs']:
                st.write(f"**Post:** {job['post']}, **Salary:** {job['salary']}")
            
            # ---------------- Step 4: Appointment Letter ----------------
            appointment_letter = f"""
            Dear {result['name']},

            Congratulations! You are selected for the position of {result['suggested_jobs'][0]['post']}.
            Your appointment letter is attached.

            Salary: {result['suggested_jobs'][0]['salary']}

            Regards,
            HR Team
            """
            st.download_button(
                label=f"Download Appointment Letter ({result['suggested_jobs'][0]['post']})",
                data=appointment_letter,
                file_name=f"Appointment_{result['name']}.txt",
                mime="text/plain"
            )
else:
    st.info("Upload a resume meeting at least 60% of the required headings to proceed to Step 2.")