import streamlit as st
import requests
from groq import Groq
from streamlit_option_menu import option_menu
from auth import create_users_table, signup_user, login_user
import datetime
import sqlite3
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import speech_recognition as sr
import os
import numpy as np
from PIL import Image
import pandas as pd
import streamlit as st
import tensorflow as tf


# ENVIRONMENT SETTINGS (before TF load)
import streamlit as st
import sqlite3
import tensorflow as tf
import os

# -----------------------------
# Database Initialization
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    return conn, conn.cursor()
def create_tables():
    conn = st.session_state.conn
    c = st.session_state.c

    # Feedback table
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        comments TEXT,
        rating INTEGER,
        date TEXT
    )
    """)
    conn.commit()

# Call this once after DB init
if "conn" not in st.session_state:
    st.session_state.conn, st.session_state.c = init_db()
    create_tables()
# -----------------------------
# TensorFlow / Keras Setup
# -----------------------------
# Force TensorFlow to use legacy Keras API
os.environ["TF_USE_LEGACY_KERAS"] = "1"

@st.cache_resource
def load_model():
    model = tf.keras.models.load_model(
        "shaheen_model_finetuned.keras",
        compile=False,
        safe_mode=False,
        custom_objects={}
    )
    return model



if "init" not in st.session_state:
    st.session_state.init = True
create_users_table()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

#test database

import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT,
    status TEXT DEFAULT 'active'
)
""")

# PREDICTIONS TABLE (THIS WAS MISSING ❌)
c.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    disease TEXT,
    confidence TEXT,
    date TEXT
)
""")

conn.commit()



# for styling


st.markdown("""
<style>

/* MAIN APP BACKGROUND */
.stApp {
    background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
                url("https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* REMOVE WHITE SPACE */
.block-container {
    padding-top: 2rem;
}

/* GLASS EFFECT */
div[data-testid="stForm"],
div[data-testid="stVerticalBlock"] {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* TITLES */
h1, h2, h3 {
    color: white !important;
    font-weight: bold;
}

/* TEXT */
p, label {
    color: white !important;
}


            
/* INPUT BOX */
div.stTextInput > div > div > input {
    background-color: #d9fdd3 !important; /* light green background */
    color: black !important;
    border: 1px solid #2e7d32 !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

/* PLACEHOLDER */
div.stTextInput > div > div > input::placeholder {
    color: #4caf50 !important; /* greenish placeholder text */
}

/* INPUT FOCUS */
div.stTextInput > div > div > input:focus {
    border: 2px solid #64dd17 !important; /* bright green border */
    outline: none !important;
    background-color: #c8f7c5 !important; /* brighter green when active */
}
            

/* BUTTONS (GLOBAL) */
div.stButton > button {
    background: linear-gradient(135deg, #43cea2, #185a9d) !important; /* green-blue gradient */
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-size: 16px !important;
    font-weight: bold !important;
    padding: 10px 16px !important;
    width: 100%;
    transition: 0.4s ease-in-out;
}

/* BUTTON HOVER (GLOBAL) */
div.stButton > button:hover {
    background: linear-gradient(135deg, #ff7eb9, #ff65a3, #7afcff, #feff9c, #fff740) !important; /* rainbow gradient */
    color: black !important;
}



/* SIDEBAR BACKGROUND */
section[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.85); /* dark glassy background */
    backdrop-filter: blur(12px);
}

/* SIDEBAR TEXT */
section[data-testid="stSidebar"] * {
    color: #90EE90 !important; /* light green text */
    font-weight: bold;
}

/* SIDEBAR NAV ITEMS */
div[role="radiogroup"] label {
    background: transparent !important; /* transparent until hover/active */
    color: #90EE90 !important;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 12px;
    transition: 0.4s ease-in-out;
    font-size: 18px !important;
    font-weight: bold !important;
    cursor: pointer !important;
}

/* HOVER EFFECT */
div[role="radiogroup"] label:hover {
    background: linear-gradient(135deg, #43cea2, #185a9d) !important; /* green-blue gradient */
    color: white !important;
    transform: scale(1.02);
}

/* ACTIVE (SELECTED) STATE */
div[role="radiogroup"] input:checked + div {
    background: linear-gradient(135deg, #ff7eb9, #ff65a3, #7afcff, #feff9c, #fff740) !important; /* rainbow gradient */
    color: black !important;
    border-radius: 12px !important;
    font-weight: bold !important;
}

/* SELECTBOX */
div[data-baseweb="select"] > div {
    background-color: rgba(0,0,0,0.8) !important;
    color: #90EE90 !important;
    font-size: 18px !important;
    font-weight: bold !important;
}

/* DROPDOWN */
ul {
    background-color: rgba(0,0,0,0.9) !important;
}

li {
    color: #90EE90 !important;
    font-size: 18px !important;
    font-weight: bold !important;
}

/* DROPDOWN HOVER */
li:hover {
    background-color: rgba(144,238,144,0.2) !important;
}
            

/* CHOOSE IMAGE BUTTON */
.stFileUploader button {
    background: linear-gradient(135deg, #43cea2, #185a9d) !important; /* professional green-blue gradient */
    color: white !important;              /* visible text */
    font-weight: bold !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 10px 18px !important;
    transition: 0.4s ease-in-out;
}

/* HOVER EFFECT */
.stFileUploader button:hover {
    background: linear-gradient(135deg, #ff7eb9, #ff65a3, #7afcff, #feff9c, #fff740) !important; /* rainbow gradient on hover */
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# INIT
# =========================
create_users_table()

st.set_page_config(
    page_title="AgriVision AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# =========================
# AUTH FUNCTIONS
# =========================
def login_page():

    st.title("🔐 Login")

    # IMPORTANT: use session_state default values
    if "email" not in st.session_state:
        st.session_state.email = ""

    if "password" not in st.session_state:
        st.session_state.password = ""

    email = st.text_input("Email", key="login_email_unique")
    password = st.text_input("Password", type="password", key="login_password_unique")

    if st.button("Login", key="login_btn_unique"):

        if login_user(email, password):

            st.session_state.logged_in = True
            st.session_state.user = email

            st.rerun()

        else:
            st.error("Invalid Email or Password")

def signup_page():

    st.title("📝 Signup")

    username = st.text_input("Create Username", key="signup_username")
    email = st.text_input("Enter Email", key="signup_email")
    password = st.text_input("Create Password", type="password", key="signup_password")

    if st.button("Signup", key="signup_btn"):

        if signup_user(username, email, password):
            st.success("Account Created Successfully")
        else:
            st.error("Username or Email Already Exists")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.rerun()

    def ask_bot(question):
        return f"You asked: {question}"

# MAIN APP
# =========================
def main_app():
    c = st.session_state.c
    conn = st.session_state.conn
    # =========================
    # CONFIG
    # =========================
    API_URL = "https://ravage-elephant-supplier.ngrok-free.dev/predict"

    client = Groq(
        api_key="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"   # ⚠️ move to st.secrets later
    )
    def ask_bot(question):
        if not question:
            return "please enter a question"
        response = client.chat.completions.create(
            model ="llama-3.1-8b-instant",
            messages=[

                {
                    "role":"system",
                    "content": "you are agriculture assistant.Always start with 'im your agriculture assistant."

                },
                {"role": "user","content": question}
            ]
        )

        return response.choices[0].message.content

    # =========================
    # SIDEBAR
    # =========================
    with st.sidebar:
        st.success(f"Welcome {st.session_state.user}")

        if st.button("Logout"):
            logout()

        selected = option_menu(
            menu_title="AgriVision AI",
            options=[
                "Dashboard",
                "Prediction",
                "Webcam",
                "Agri Bot",
                "History",
                "About"
            ],
            icons=[
                "house",
                "search",
                "camera",
                "robot",
                "clock-history",
                "info-circle"
            ],
            menu_icon="leaf",
            default_index=0
        )

    # =========================
    # DASHBOARD
    # =========================
    if selected == "Dashboard":
        st.title("🌿 AgriVision AI")
        st.subheader("Smart Agriculture Monitoring System")
        st.write(f"👋 Welcome, {st.session_state.user}")

        # --- Summary cards ---
        c = st.session_state.c
        c.execute("SELECT COUNT(*) FROM predictions WHERE username=?", (st.session_state.user,))
        total_predictions = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM predictions WHERE username=? AND disease!='Healthy'", (st.session_state.user,))
        diseases_detected = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM feedback WHERE username=?", (st.session_state.user,))
        feedback_submitted = c.fetchone()[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Predictions", total_predictions)
        col2.metric("Diseases Detected", diseases_detected)
        col3.metric("Feedback Submitted", feedback_submitted)

        # --- Recent activity log ---
        c.execute("""
            SELECT disease, confidence, date
            FROM predictions
            WHERE username=?
            ORDER BY date DESC
            LIMIT 5
        """, (st.session_state.user,))
        rows = c.fetchall()
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows, columns=["Disease", "Confidence", "Date"])
            st.subheader("🕒 Recent Activity")
            st.table(df)
        else:
            st.info("No recent predictions found.")

        # --- Feedback form ---
        st.subheader("💬 Submit Feedback")
        with st.form("feedback_form"):
            comments = st.text_area("Your comments")
            rating = st.slider("Rating (1-5)", 1, 5)
            submitted = st.form_submit_button("Submit")

            if submitted:
                c.execute(
                    "INSERT INTO feedback (username, comments, rating, date) VALUES (?, ?, ?, DATE('now'))",
                    (st.session_state.user, comments, rating)
                )
                st.session_state.conn.commit()
                st.success("Thank you for your feedback!")

        # --- Quick actions ---
        st.subheader("⚡ Quick Actions")
        colA, colB = st.columns(2)
        if colA.button("Upload Image"):
            st.session_state.page = "Prediction"
        if colB.button("Ask Agri Bot"):
            st.session_state.page = "Agri Bot"

    # =========================
    # PREDICTION
    # =========================
    elif selected == "Prediction":
        st.subheader("🔍 Plant Disease Detection")

        uploaded_file = st.file_uploader("Choose image", type=["jpg", "png", "jpeg"], key="prediction_uploader")

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image")

            if st.button("Predict Disease"):
                try:
                    with st.spinner("Analyzing image..."):
                        response = requests.post(API_URL, files={"file": uploaded_file}, timeout=60)

                    if response.status_code == 200:
                        result = response.json()
                        disease = result.get("prediction", "Unknown")
                        confidence = result.get("confidence", "N/A")

                        st.success(f"Prediction: {disease}")
                        st.info(f"Confidence: {confidence}%")

                        # SAVE TO DATABASE
                        c.execute("""
                            INSERT INTO predictions (username, disease, confidence, date)
                            VALUES (?, ?, ?, ?)
                        """, (st.session_state.user, disease, str(confidence), str(datetime.date.today())))
                        conn.commit()
                    else:
                        st.error(f"Prediction Failed ({response.status_code})")
                except Exception as e:
                    st.error(f"Error: {e}")

    # =========================
    # WEBCAM
    # =========================
    elif selected == "Webcam":
        st.subheader("📷 Live Plant Diagnosis")

        camera = st.camera_input("Capture Plant Image")

        if camera:
            st.image(camera)
            img = Image.open(camera)
            img_array = np.array(img)
            brightness = np.mean(img_array)

            if brightness < 20:
                st.error("Image too dark. Capture plant clearly.")
                st.stop()

            if st.button("Predict Webcam Image", key="webcam_predict_btn"):
                try:
                    with st.spinner("Analyzing..."):
                        response = requests.post(API_URL, files={"file": camera}, timeout=60)

                    if response.status_code == 200:
                        result = response.json()
                        prediction = result.get("prediction", "Unknown")
                        confidence = float(result.get("confidence", 0))

                        if confidence < 70:
                            st.warning("Low confidence prediction. Retake image.")
                        else:
                            st.success(f"Prediction: {prediction}")
                            st.info(f"Confidence: {confidence:.2f}%")
                    else:
                        st.error("Prediction Failed")
                except Exception as e:
                    st.error(f"Error: {e}")

    # =========================
    # AGRI BOT
    # =========================
    elif selected == "Agri Bot":
        st.subheader("🤖 Agriculture Assistant")

    question = st.text_area(
        "Ask your farming question",
        key="agri_text"
    )

    if st.button("Get Answer"):
        if question.strip():
            answer = ask_bot(question)
            st.success(answer)

    if st.button("🎤 Speak your question"):

        try:
            recognizer = sr.Recognizer()

            with sr.Microphone() as source:
                st.info("Listening... please speak")
                audio = recognizer.listen(source)

            spoken_text = recognizer.recognize_google(audio)

            st.success(f"You said: {spoken_text}")

            answer = ask_bot(spoken_text)

            st.success(answer)

        except Exception:
            st.warning(
                "Voice feature unavailable. Please use text input."
            )

    # =========================
    # HISTORY
    # =========================
    elif selected == "History":
        st.subheader("📜 Prediction History")

        c = st.session_state.c
        c.execute("""
            SELECT id, disease, confidence, date
            FROM predictions
            WHERE username = ?
            ORDER BY date DESC
        """, (st.session_state.user,))
        rows = c.fetchall()

        if rows:
            import pandas as pd
            df = pd.DataFrame(rows, columns=["ID", "Disease", "Confidence", "Date"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No history found yet.")

    # =========================
    # ABOUT
    # =========================
    elif selected == "About":
        st.subheader("ℹ️ About AgriVision AI")
        st.markdown("""
        ### 🌿 AgriVision AI

        AgriVision AI is an intelligent agriculture monitoring system designed to help farmers, students, and researchers detect plant diseases using Artificial Intelligence.

        ### 🎯 Project Goal
        Empower agriculture with AI-driven disease detection for faster and more accurate plant health monitoring.

        ### 🚀 Features
        ✅ Plant Disease Detection using CNN Model  
        ✅ Image Upload Prediction System  
        ✅ Real-Time Webcam Diagnosis  
        ✅ AI Agriculture Assistant (Agri Bot)  
        ✅ Prediction History Tracking  
        ✅ User Authentication System  

        ### 🧠 Technologies Used
        - Python  
        - Streamlit  
        - CNN / Deep Learning  
        - Transfer Learning  
        - SQLite Database  
        - Groq API  
        - OpenCV / Webcam Integration  

        ### 🌱 Benefits
        • Early disease detection  
        • Reduced crop loss  
        • Faster diagnosis  
        • Easy-to-use interface  
        • Supports smart farming practices  

        ### 👨‍💻 Developed For
        Final Year Project (FYP) — Smart AI Assistant and Plant Disease Detection System
        """)

# =========================
# ROUTING (IMPORTANT FIX)
# =========================
if st.session_state.logged_in:
    main_app()
else:
    choice = st.sidebar.selectbox("Select Option", ["Login", "Signup"])

    if choice == "Login":
        login_page()
    else:
        signup_page()
 

