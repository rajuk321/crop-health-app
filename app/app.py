import streamlit as st
def is_leaf(image):
    import numpy as np
    import cv2

    img = np.array(image)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # GREEN MASK
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    green_ratio = np.sum(mask > 0) / mask.size

    # RGB analysis
    avg_color = np.mean(img, axis=(0,1))
    r, g, b = avg_color

    # 🔥 SMART CONDITIONS
    if green_ratio < 0.08:   # बहुत कम green → reject
        return False

    if g < r:  # green dominant नहीं → reject (human mostly red/skin tone)
        return False

    return True
def set_bg(image_url):
    st.markdown(f"""
    <style>
    .stApp {{
        background: url("{image_url}") no-repeat center center fixed;
        background-size: cover;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.7);
        z-index: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """, unsafe_allow_html=True)
import tensorflow as tf
import numpy as np
import pickle
from PIL import Image
import sqlite3
import requests
import datetime
import os
import random
import streamlit.components.v1 as components
import smtplib
from email.message import EmailMessage
from auth import *  
from farmer_profile import *
from location import *
from voice import *
from weather import show_weather
from login_ui import login_page
from fpdf import FPDF
import pandas as pd


st.set_page_config(page_title="Crop Health App", layout="wide")
def set_bg_all():
    st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef") no-repeat center center fixed;
        background-size: cover;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.7);
        z-index: 0;
    }

    .block-container {
        position: relative;
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)
# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
   st.session_state.page = "login"
# ---------------- LOGIN ----------------
set_bg_all()   # ✅ ADD THIS
if not st.session_state.get("user"):
    login_page()
    st.stop()

# ✅ CSS LOGIN KE BAAD
st.markdown("""
<style>
.feature-card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)
   

# ---------------- DASHBOARD ----------------
# ---------------- DASHBOARD ----------------
if st.session_state.page == "dashboard":
       # 🔴 LOGOUT BUTTON (TOP RIGHT)
   
    set_bg("https://images.unsplash.com/photo-1500382017468-9049fed747ef")
    # 🔥 FIXED BACKGROUND (WORKING)
    st.markdown("""
    <style>

    /* MAIN BACKGROUND */
    .stApp {
        background: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef") no-repeat center center fixed;
        background-size: cover;
    }

    /* DARK OVERLAY */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.7);
        z-index: 0;
    }

    /* CONTENT ABOVE */
    .block-container {
        position: relative;
        z-index: 1;
    }

    </style>
    """, unsafe_allow_html=True)
    
    # ---------------- UI ----------------
    if st.session_state.page == "dashboard":
     st.title("🌱 Crop Health & Yield Prediction")
     
    
    menu = [
        ("👤", "Profile", "Manage your farm profile"),
        ("🌿", "Disease Detection", "Check crop health"),
        ("🌾", "Yield Prediction", "Predict crop yield"),
        ("🌦️", "Weather", "Check weather updates"),
        ("🎤", "Voice Assistant", "Ask using voice"),
        ("📊", "History", "View past records")
    ]

    cols = st.columns(3)

    for i, (icon, title, desc) in enumerate(menu):

        with cols[i % 3]:

            st.markdown(f"""
            <div style="
                background: rgba(0,0,0,0.6);
                padding:20px;
                border-radius:15px;
                backdrop-filter: blur(5px);
            ">
                <h2>{icon}</h2>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(title, key=title):
               st.session_state.page = title
               st.rerun()
    # ================= LOGOUT SECTION =================

    st.markdown("""
    <div style="margin-top:50px;"></div>
    """, unsafe_allow_html=True)

    # Center logout button
    col1, col2, col3 = st.columns([3,2,3])

    with col2:
       if st.button("🚪 Logout", use_container_width=True):
          st.session_state.user = None 
          st.session_state.page = "login"
          st.rerun()         
# ---------------- GPS ----------------
def gps():
    components.html("""
    <script>
    navigator.geolocation.getCurrentPosition(
    (pos)=>{
        document.write(pos.coords.latitude + "," + pos.coords.longitude)
    })
    </script>
    """, height=50)

    gps()

# ---------------- PATH ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISEASE_MODEL_PATH = os.path.join(BASE_DIR,"models","disease_model.h5")
YIELD_MODEL_PATH = os.path.join(BASE_DIR,"models","yield_model.pkl")

# ---------------- LOAD MODELS ----------------
@st.cache_resource
def load_disease_model():
    return tf.keras.models.load_model(
        DISEASE_MODEL_PATH,
        compile=False,
        safe_mode=False
    )

disease_model = load_disease_model()
@st.cache_resource
def load_yield_model():
    return pickle.load(open(YIELD_MODEL_PATH,"rb"))

yield_model = load_yield_model()
# ---------------- DATABASE ----------------
conn = sqlite3.connect("history.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS history(
date TEXT,
result TEXT,
confidence REAL
)
""")
conn.commit()

create_profile_table()

# ---------------- SATELLITE ----------------
def satellite_health():
    return random.choice(["Healthy","Moderate Stress","High Stress"])
def generate_pdf(name, crop, disease, medicine):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Crop Health Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.cell(200, 10, txt=f"Farmer: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Crop: {crop}", ln=True)
    pdf.cell(200, 10, txt=f"Disease: {disease}", ln=True)
    pdf.cell(200, 10, txt=f"Medicine: {medicine}", ln=True)
    
    pdf.output("report.pdf")
def send_email(receiver_email):

    email = EmailMessage()
    email['Subject'] = "Crop Health Report"
    email['From'] = "yourgmail@gmail.com"
    email['To'] = receiver_email

    email.set_content("Please find attached crop health report.")

    with open("report.pdf", "rb") as f:
        file_data = f.read()
        email.add_attachment(file_data, maintype='application', subtype='pdf', filename="report.pdf")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("rajukumar9353r@gmail.com", "wjns bvmn fzkv cakc")
        smtp.send_message(email)
# ---------------- TABS ----------------


# ================= PROFILE =================
if st.session_state.page == "Profile":
    set_bg("https://images.unsplash.com/photo-1592982537447-7440770cbfc9")
    # 🔙 Back Button
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    # 👇 YE BUTTON KE BAHAR HONA CHAHIYE
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("👤 Farmer Profile")

    # 🔹 PLAN TYPE
    plan = st.radio(
        "💼 Select Plan",
        ["Free 🌿", "Pro 🚀", "Premium 👑"],
        horizontal=True
    )

    st.markdown("---")

    # 🔹 FORM
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("👤 Farmer Name", placeholder="Enter your name")
        crop = st.selectbox("🌱 Crop", ["Tomato","Rice","Potato","Sugarcane"])

    with col2:
        soil = st.selectbox("🟤 Soil Type", ["Black","Red","Clay","Sandy"])
        loc  = st.text_input("📍 Farm Location", placeholder="Enter location")

    st.markdown("---")

    # 🔹 BUTTONS
    col3, col4 = st.columns(2)

    with col3:
        if st.button("💾 Save Profile"):
            save_profile(name, crop, soil, loc)
            st.success("Profile Saved ✅")

    with col4:
        if st.button("📂 Show Profile"):
            data = get_profile()
            st.session_state.profile_data = data

    st.markdown('</div>', unsafe_allow_html=True)

    # 🔥 PROFILE PREVIEW
    if "profile_data" in st.session_state:

        data = st.session_state.profile_data

        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.05);
            padding:20px;
            border-radius:15px;
            margin-top:15px;
            border-left:5px solid #22c55e;
        ">
            <h4>👤 {data[0]}</h4>
            🌱 Crop: {data[1]} <br>
            🟤 Soil: {data[2]} <br>
            📍 Location: {data[3]} <br>
            💼 Plan: {plan}
        </div>
        """, unsafe_allow_html=True)

# ================= DISEASE =================
elif st.session_state.page == "Disease Detection":
    set_bg("https://images.unsplash.com/photo-1500382017468-9049fed747ef")

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

   
    option = st.radio("Select Input", ["Upload", "Camera"])
    crop_name = st.selectbox("🌱 Select Crop", ["Apple", "grape", "Potato", "Tomato"])
    image = None

    # Upload
    if option == "Upload":
        file = st.file_uploader("Upload Leaf Image")
        if file:
            image = Image.open(file)

    # Camera
    else:
        cam = st.camera_input("Take Photo")
        if cam:
            image = Image.open(cam)

    # ================= MAIN LOGIC =================
    if image:

        # ✅ STEP 1: Leaf Validation
        if not is_leaf(image):
             st.warning("⚠️ Image may not be a leaf. Trying prediction anyway...")
             st.stop()
             
        # Preprocess
        img = image.resize((128, 128))
        img = img.convert("RGB")

        arr = np.array(img) / 255.0
        arr = arr.reshape(1, 128, 128, 3)

        # Prediction
        pred = disease_model.predict(arr)[0][0]

        confidence = pred * 100 if pred > 0.5 else (1 - pred) * 100

        # ✅ STEP 2: Confidence Check
        if confidence < 70:
           st.warning("⚠️ Image unclear, try better leaf photo")
           st.stop()

        # Prediction Logic
        if pred > 0.5:
            status = "Healthy"
            disease = "healthy"
        else:
            status = "Diseased"
            disease = "Disease Detected (Type Unknown)"

        leaf = f"{crop_name} Leaf"

        # Disease Info
        disease_info = {
            "early_blight": {
                "deficiency": "Nitrogen & Potassium deficiency",
                "water": "Moderate watering needed",
                "medicine": "Mancozeb spray",
                "quantity": "2g per liter water"
            },
            "healthy": {
                "deficiency": "No deficiency",
                "water": "Normal watering",
                "medicine": "No medicine needed",
                "quantity": "-"
            }
        }

        info = disease_info.get(disease, {
          "deficiency": "Nitrogen & Potassium imbalance detected",
          "water": "Moderate irrigation required (2-3 times/week)",
          "medicine": "Mancozeb fungicide spray recommended",
          "quantity": "2 grams per liter of water (spray every 7 days)"
       })

        # OUTPUT
        if status == "Healthy":
            st.success(f"✅ Status: Healthy ({confidence:.2f}%)")
        else:
            st.error(f"⚠️ Status: Diseased ({confidence:.2f}%)")

        st.info(f"🌿 Leaf: {leaf}")

        if status == "Diseased":
            st.warning(f"🦠 Disease: {disease}")

        st.warning(f"🧪 Deficiency: {info['deficiency']}")
        st.info(f"💧 Water Need: {info['water']}")
        st.success(f"💊 Medicine: {info['medicine']}")
        st.info(f"📏 Quantity: {info['quantity']}")

        # ================= EMAIL =================
        st.subheader("📧 Send Report")

        email_input = st.text_input("Enter Email Address")

        if st.button("Send Report to Email"):
            if email_input:
                name = "Farmer"
                crop = leaf

                generate_pdf(name, crop, disease, info["medicine"])
                send_email(email_input)

                st.success("Email Sent Successfully ✅")
            else:
                st.warning("Please enter email")
# ================= YIELD =================
elif st.session_state.page == "Yield Prediction":
     set_bg("https://images.unsplash.com/photo-1500382017468-9049fed747ef")
     if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
     # Load model + columns
      # Load model & columns
     yield_model = pickle.load(open("models/yield_model.pkl", "rb"))
     columns = pickle.load(open("models/columns.pkl", "rb"))

     st.subheader(" Yield Prediction")

     rainfall = st.slider("Rainfall (mm)", 0, 500)
     temperature = st.slider("Temperature (°C)", 0, 50)
     fertilizer = st.slider("Fertilizer (kg)", 0, 200)
     humidity = st.slider("Humidity (%)", 0, 100)

     soil = st.selectbox("Soil Type", ["clay", "sandy", "loamy"])
     crop = st.selectbox("Crop", ["wheat", "rice", "maize"])

     if st.button("Predict Yield"):
          # Step 1: Input data define karo
          input_data = {
            "rainfall": rainfall,
            "temperature": temperature,
            "fertilizer": fertilizer,
            "humidity": humidity,
            f"soil_type_{soil}": 1,
            f"crop_{crop}": 1
         }

         # Step 2: DataFrame banao
          df = pd.DataFrame([input_data])

            # Step 3: Columns match karo
          df = df.reindex(columns=columns, fill_value=0)

            # Step 4: Prediction
          prediction = yield_model.predict(df)[0]

           # Step 5: Output
          st.success(f"🌱 Predicted Yield: {prediction:.2f} ton/hectare")

           # Step 6: Suggestion
          if prediction < 2:
           st.warning("⚠️ Low Yield - Improve fertilizer or irrigation")
          else:
           st.success("✅ Good Yield Expected")
# ================= SATELLITE + WEATHER =================
elif st.session_state.page == "Weather":
    set_bg("https://images.unsplash.com/photo-1500674425229-f692875b0ab7")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    show_weather()

    

    if st.button("Satellite Health"):
        st.info(satellite_health())

# ================= VOICE =================
elif st.session_state.page == "Voice Assistant":
    set_bg("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    if st.button("Speak"):

       question = listen()

       if question:

          answer = ai_answer(question)

          st.success(answer)

          try:
             speak(answer)
          except:
           pass

       else:
            st.error("Voice detect नहीं हुई, फिर से बोलें")
# ================= HISTORY =================
elif st.session_state.page == "History":
    set_bg("https://images.unsplash.com/photo-1504384308090-c894fdcc538d")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📊 Prediction History")

    rows = c.execute("SELECT * FROM history").fetchall()

    if rows:

        import pandas as pd

        df = pd.DataFrame(rows, columns=["Date", "Result", "Confidence"])

        # 🔹 Convert types
        df["Confidence"] = pd.to_numeric(df["Confidence"], errors='coerce')
        # 🔹 FILTER
        filter_option = st.selectbox("🔍 Filter", ["All", "Healthy", "Diseased"])

        if filter_option != "All":
            df = df[df["Result"] == filter_option]

        # 🔹 STATS
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Records", len(df))
        col2.metric("Healthy", len(df[df["Result"]=="Healthy"]))
        col3.metric("Diseased", len(df[df["Result"]=="Diseased"]))

        st.markdown("---")

        # 🔥 CARD STYLE HISTORY
        for i, row in df.iloc[::-1].iterrows():

            if row["Result"] == "Healthy":
                color = "#22c55e"
                icon = "✅"
            else:
                color = "#ef4444"
                icon = "⚠️"

            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                padding:15px;
                border-radius:12px;
                margin-bottom:10px;
                border-left:5px solid {color};
            ">
                <b>{icon} {row['Result']}</b><br>
                📅 {row['Date']} <br>
                🎯 Confidence: {row['Confidence']:.2f}%
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("No history found")

    st.markdown('</div>', unsafe_allow_html=True)