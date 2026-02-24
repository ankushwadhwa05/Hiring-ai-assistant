import streamlit as st
import os
import json
from datetime import datetime
from textblob import TextBlob
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables (for local testing with .env file)
load_dotenv()

# 1. Configuration & UI Styling
st.set_page_config(page_title="Hiring Assistant", page_icon="AI", layout="wide")

# Custom CSS for UI Enhancements & Top-Left Title
st.markdown("""
<style>
    /* Top-left persistent header */
    [data-testid="stHeader"]::after {
        content: "Automated Hiring Assistant";
        font-size: 18px;
        font-weight: 600;
        color: #888;
        position: absolute;
        top: 20px;
        left: 60px; /* Pushed right so it doesn't overlap the sidebar menu icon */
    }
    /* Animated Hourglass */
    @keyframes flip-hourglass {
        0% { transform: rotate(0deg); }
        50% { transform: rotate(180deg); }
        100% { transform: rotate(180deg); }
    }
    .animated-hourglass {
        display: inline-block;
        animation: flip-hourglass 2s infinite ease-in-out;
    }
    .stChatFloatingInputContainer { padding-bottom: 20px; }
    .stChatMessage { border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    .dashboard-text { font-size: 14px; color: #555; }
</style>
""", unsafe_allow_html=True)

# 2. Performance Optimization (Caching Client)
@st.cache_resource
def get_genai_client():
    """Caches the GenAI client to improve performance across reruns."""
    # 1. First, try to get the key from your .env file (Local Testing)
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # 2. If not found, safely try Streamlit secrets (Cloud Deployment)
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except (FileNotFoundError, KeyError):
            pass # Ignore the error if the secrets file doesn't exist locally
            
    # 3. If we STILL don't have a key, stop the app and warn the user
    if not api_key:
        st.error("API Key not found. Please make sure your .env file is set up correctly with GEMINI_API_KEY.")
        st.stop()
        
    return genai.Client(api_key=api_key)

client = get_genai_client()
# ==========================================
# 3. State Management
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stage" not in st.session_state:
    st.session_state.stage = "greeting"
if "sentiment" not in st.session_state:
    st.session_state.sentiment = "Neutral 😐"

EXIT_KEYWORDS = ["quit", "exit", "goodbye", "bye", "stop"]
REQUIRED_FIELDS = [
    "Full Name", "Email Address", "Phone Number", 
    "Years of Experience", "Desired Position", 
    "Current Location", "Tech Stack"
]

# ==========================================
# 4. Sidebar: Recruiter Dashboard & Settings
# ==========================================
with st.sidebar:
    st.header("⚙️ Settings & Dashboard")
    
    # Multilingual Support
    selected_language = st.selectbox(
        "Interview Language", 
        ["English", "Spanish", "French", "German", "Hindi", "Mandarin"]
    )
    
    st.divider()
    
    # Sentiment Analysis Display
    st.subheader("Live Candidate Sentiment")
    if "Positive" in st.session_state.sentiment:
        st.success(st.session_state.sentiment)
    elif "Negative" in st.session_state.sentiment:
        st.error(st.session_state.sentiment)
    else:
        st.info(st.session_state.sentiment)
        
    st.markdown("<p class='dashboard-text'>Sentiment is analyzed in real-time based on the candidate's latest response.</p>", unsafe_allow_html=True)
    st.divider()
    
    # Live Interview Status
    st.subheader("Interview Status")
    
    # Visual status indicator
    # Visual status indicator
    if st.session_state.stage == "greeting":
        st.info("Status: Waiting to Start")
    elif st.session_state.stage == "gathering":
        # Custom animated warning box
        st.markdown("""
        <div style='background-color: #fff5e6; padding: 15px; border-radius: 8px; color: #0f0e0e; font-weight: 500;'>
            Status: Phase 1 - Gathering Details <span class='animated-hourglass'>⏳</span>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.stage == "tech_questions":
        st.success("Status: Phase 2 - Technical Assessment ")
    elif st.session_state.stage == "ended":
        st.error("Status: Interview Concluded ")

# ==========================================
# 5. Prompt Engineering 
# ==========================================
def get_system_instruction(language):
    base_prompt = f"""You are the TalentScout Hiring Assistant, an AI recruiter. 
    Crucial Rule: You MUST communicate entirely in {language}. 
    Tone: Professional, welcoming, and empathetic. 
    Personalization Rule: If the user provides their name or location, seamlessly use it in your next responses to build rapport.
    Guardrail: Do not answer coding questions for the user. Stick strictly to the interview process.
    """
    
    if st.session_state.stage in ["greeting", "gathering"]:
        return base_prompt + f"""
        Current Objective: Gather these details: {', '.join(REQUIRED_FIELDS)}.
        Ask for 1 or 2 items at a time. Acknowledge their answers contextually (e.g., if they have 10 years of experience, compliment them on their extensive background).
        Once you have ALL the information, output the exact phrase "TRANSITION_TO_TECH" at the very end of your message, and ask if they are ready for technical questions based on their tech stack.
        """
    elif st.session_state.stage == "tech_questions":
        return base_prompt + """
        Current Objective: Generate 3 to 5 relevant technical interview questions based strictly on the tech stack they provided earlier.
        Ask them one by one. Evaluate their answer briefly before asking the next.
        Once all questions are done, output the exact phrase "END_INTERVIEW" at the very end of your message, thank the candidate by name, and state a recruiter will contact them.
        """
    else:
        return base_prompt + "The interview is over. Politely say goodbye."

# ==========================================
# 6. Sentiment Analysis Helper
# ==========================================
def analyze_sentiment(text):
    """Gauges candidate emotion using TextBlob."""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.2:
        return "Positive 🙂"
    elif polarity < -0.2:
        return "Negative 😟"
    else:
        return "Neutral 😐"

# ==========================================
# Simulated Database Backend
# ==========================================
def save_interview_data(messages, sentiment):
    """Simulates a backend database by saving the interview transcript to a JSON file."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "final_sentiment": sentiment,
        "transcript": messages
    }
    
    db_filename = "simulated_backend_db.json"
    
    # Load existing data if the file exists, otherwise start an empty list
    try:
        with open(db_filename, "r") as f:
            db = json.load(f)
    except FileNotFoundError:
        db = []
        
    db.append(record)
    
    # Save the updated list back to the file
    with open(db_filename, "w") as f:
        json.dump(db, f, indent=4)

# ==========================================
# 7. Main Chat Interface
# ==========================================
st.title("Hiring Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Initial Greeting
if not st.session_state.messages and st.session_state.stage == "greeting":
    greeting = f"Hello! I am the Hiring Assistant. Let's get started. Could you please provide your Full Name? (Operating in {selected_language})"
    st.session_state.messages.append({"role": "model", "content": greeting})
    st.session_state.stage = "gathering"
    st.rerun()

# Handle User Input
if prompt := st.chat_input("Type your message here..."):
    # 1. Check Exit Keywords
    if any(keyword in prompt.lower() for keyword in EXIT_KEYWORDS):
        st.session_state.stage = "ended"
        st.session_state.messages.append({"role": "user", "content": prompt})
        goodbye_msg = "Thank you for your time. The conversation has been ended. Our HR will review your file and contact you shortly."
        st.session_state.messages.append({"role": "model", "content": goodbye_msg})
        st.rerun()

    # 2. Analyze Sentiment
    st.session_state.sentiment = analyze_sentiment(prompt)

    # 3. Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.stage == "ended":
        st.warning("The interview has concluded. Please refresh to start over.")
        st.stop()

    # 4. Generate LLM Response with UI Spinner for perceived performance
    with st.chat_message("model"):
        with st.spinner("Analyzing profile..."):
            try:
                contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=get_system_instruction(selected_language),
                        temperature=0.4 
                    )
                )
                
                bot_reply = response.text
                
                # Logic hooks
                if "TRANSITION_TO_TECH" in bot_reply:
                    st.session_state.stage = "tech_questions"
                    bot_reply = bot_reply.replace("TRANSITION_TO_TECH", "").strip()
                    st.toast('Candidate Profile Captured! Initializing Technical Assessment...')
                    
                if "END_INTERVIEW" in bot_reply:
                    st.session_state.stage = "ended"
                    bot_reply = bot_reply.replace("END_INTERVIEW", "").strip()
                    
                    # Save the data to our simulated database
                    save_interview_data(st.session_state.messages, st.session_state.sentiment)

                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "model", "content": bot_reply})
                
           except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                    st.warning("The AI is thinking a bit too fast! We hit the free-tier rate limit (15 messages/minute). Please wait 60 seconds and try your message again.")
                else:
                    st.error(f"Connection error. Please try again. (Error: {e})")
