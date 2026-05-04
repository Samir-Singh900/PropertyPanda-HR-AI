import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf

# --- 1. CONFIGURATION ---
# IMPORTANT: Safely pull the key from Streamlit's backend, NOT the public code
API_KEY = st.secrets["GEMINI_API_KEY"] 
genai.configure(api_key=API_KEY)

# Streaming function for blazing fast, live-typing output
def stream_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        yield chunk.text

# Function to extract text from the uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += str(reader.pages[page].extract_text())
    return text

# --- 2. USER INTERFACE & THEMING ---
st.set_page_config(page_title="PropertyPanda AI Recruiter", page_icon="🐼", layout="wide")

# Custom CSS to make it look like expensive enterprise software
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E63946; color: white; font-weight: bold; border: none; font-size: 16px;}
    .stButton>button:hover { background-color: #D62828; transform: scale(1.02); transition: 0.2s;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ADVANCED HR CONTROLS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135673.png", width=80)
    st.title("⚙️ HR Operations")
    
    st.markdown("### 1. Select Mode:")
    app_mode = st.radio(
        "What should the AI do?",
        ("🎯 JD Screening & Onboarding", "🔍 Talent Discovery Mode")
    )
    
    st.divider()
    
    st.markdown("### 2. Screening Settings:")
    strict_mode = st.toggle("🚨 Strict Mode (High Standards)", value=False)
    local_context = st.toggle("🏙️ Local Market Fit (Surat)", value=True)
    
    st.divider()
    st.caption("👨‍💻 **Architect:** Samir Singh")
    st.caption("🚀 **Role:** Engineering Intern")

# --- MAIN DASHBOARD ---
st.title(f"🐼 PropertyPanda Smart HR | {app_mode.split(' ')[1]}")

col1, col2 = st.columns(2)

# Conditionally show the JD box based on the mode selected
with col1:
    if app_mode == "🎯 JD Screening & Onboarding":
        st.markdown("### 📝 Job Details")
        jd = st.text_area("Target Job Description (JD)", placeholder="Paste the job requirements here...", height=200)
    else:
        st.info("💡 **Talent Discovery Active:** No JD required. Upload a resume, and the AI will analyze the candidate's skills to recommend the Top 3 best-fitting roles within PropertyPanda or the market.")
        jd = None

with col2:
    st.markdown("### 📄 Candidate File")
    uploaded_file = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])

st.divider()

# --- 3. THE AI BRAIN ---
if st.button("⚡ Run Enterprise AI Engine"):
    if uploaded_file:
        if app_mode == "🎯 JD Screening & Onboarding" and not jd:
            st.warning("⚠️ Please provide a Job Description for screening mode.")
        else:
            try:
                resume_text = input_pdf_text(uploaded_file)
                
                # Apply HR settings
                tone = "Be highly critical." if strict_mode else "Be objective."
                location = "Evaluate if their experience aligns with the Surat real estate market." if local_context else ""
                
                # --- PROMPT 1: SCREENING & INTERVIEW MODE ---
                if app_mode == "🎯 JD Screening & Onboarding":
                    master_prompt = f"""
                    You are Deepika, Head HR at PropertyPanda. {tone} {location}
                    
                    JD: {jd}
                    RESUME: {resume_text}
                    
                    Provide a highly professional report using this EXACT markdown structure:
                    
                    ## 📊 Match Score: [Insert Number]%
                    **Executive Verdict:** [1 sentence whether to proceed or reject]
                    
                    ---
                    ### 💪 Key Strengths
                    * [Point 1]
                    * [Point 2]
                    
                    ### ⚠️ Critical Gaps
                    * [Point 1]
                    * [Point 2]
                    
                    ---
                    ### 🎤 Custom Interview Questions (Targeting Gaps)
                    1. [Technical/Hard skill question based on resume]
                    2. [Scenario question based on real estate/sales]
                    3. [Behavioral question]
                    
                    ---
                    ### ✉️ Auto-Drafted Action Email
                    [Write a professional email to the candidate. Accept for interview if score > 70%, polite rejection if < 70%. Leave placeholders for names.]
                    """
                
                # --- PROMPT 2: TALENT DISCOVERY MODE ---
                else:
                    master_prompt = f"""
                    You are a Senior Talent Acquisition Director at PropertyPanda. {tone}
                    Analyze this candidate's resume and determine the TOP 3 job titles they are actually best suited for, even if they applied for something else.
                    
                    RESUME: {resume_text}
                    
                    Use this EXACT markdown structure:
                    
                    ## 🌟 Talent Discovery Profile
                    **True Professional Identity:** [1-2 sentences summarizing their actual skill set]
                    
                    ---
                    ### 🏆 Recommended Role #1: [Insert Job Title]
                    * **Confidence:** [Insert %]
                    * **Why they fit:** [Explain based on specific resume experience]
                    
                    ### 🥈 Recommended Role #2: [Insert Job Title]
                    * **Confidence:** [Insert %]
                    * **Why they fit:** [Explain based on specific resume experience]
                    
                    ### 🥉 Recommended Role #3: [Insert Job Title]
                    * **Confidence:** [Insert %]
                    * **Why they fit:** [Explain based on specific resume experience]
                    
                    ---
                    ### 💡 HR Strategy Advice
                    [1 paragraph advising PropertyPanda leadership on how to best utilize this candidate's unique skills to grow the company]
                    """
                
                # The Output Container
                with st.container(border=True):
                    st.write("### 📡 Live AI Analysis Feed...")
                    response_stream = stream_gemini_response(master_prompt)
                    st.write_stream(response_stream)
                
                st.success("✅ Analysis Complete! Data is ready for HR review.")
                
            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")
    else:
        st.warning("⚠️ Please upload a Candidate Resume to start.")
