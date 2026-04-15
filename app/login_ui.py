import streamlit as st
from pymongo import MongoClient

import random
import smtplib
from email.message import EmailMessage

st.markdown("""
<style>

/* NORMAL BUTTON */
.stButton > button {
    background-color: transparent;
    color: white;
    border: 1px solid #555;
    border-radius: 10px;
    padding: 8px 16px;
    transition: 0.3s;
}

/* HOVER EFFECT 🔥 */
.stButton > button:hover {
    background-color: #22c55e;   /* green */
    color: white;
    border: 1px solid #22c55e;
    transform: scale(1.05);
}

/* CLICK EFFECT */
.stButton > button:active {
    transform: scale(0.95);
}

</style>
""", unsafe_allow_html=True)
# ---------------- OTP FUNCTIONS ----------------
def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(receiver_email, otp):
    email = EmailMessage()
    email['Subject'] = "Password Reset OTP"
    email['From'] = "rajukumar9353r@gmail.com"
    email['To'] = receiver_email

    email.set_content(f"Your OTP is: {otp}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("rajukumar9353r@gmail.com", "wjns bvmn fzkv cakc")
        smtp.send_message(email)


# ---------------- MAIN FUNCTION ----------------
def login_page():
     # ✅ ADD THIS (VERY IMPORTANT)
    if "page" not in st.session_state:
        st.session_state.page = "login"
    # ---------- SESSION ----------
    if "otp" not in st.session_state:
        st.session_state.otp = None

    if "reset_email" not in st.session_state:
        st.session_state.reset_email = None

   

    if "user" not in st.session_state:
        st.session_state.user = None

    def switch(page):
        st.session_state.page = page
        st.rerun()

    # ---------- MongoDB ----------
    client = MongoClient("mongodb://localhost:27017/")
    db = client["crop_project"]
    users_collection = db["users"]
    users_collection.create_index("email", unique=True)

    # ======================================================
    # LOGIN PAGE
    # ======================================================
    if st.session_state.get("page") == "login":
      
     col1, col2, col3 = st.columns([1,2,1])

     with col2:
        st.title("Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            user = users_collection.find_one({
                "email": email,
                "password": password
            })

            if user:
                st.session_state.user = user["name"]
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid Email or Password")

        if st.button("Forgot Password"):
            switch("forgot")

        if st.button("Create Account"):
            switch("register")

    # ======================================================
    # REGISTER PAGE
    # ======================================================
    elif st.session_state.get("page") == "register":

     col1, col2, col3 = st.columns([1,2,1])

     with col2:
        st.title("Register")

        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Register"):

            if password != confirm:
                st.error("Passwords do not match")

            else:
                user = users_collection.find_one({"email": email})

                if user:
                    st.error("⚠️ Email already registered")

                else:
                    users_collection.insert_one({
                        "name": name,
                        "email": email,
                        "password": password
                    })

                    st.success("Account created successfully 🎉")

        if st.button("Back to Login"):
            switch("login")

    # ======================================================
    # FORGOT PASSWORD PAGE (OTP SYSTEM)
    # ======================================================
    elif st.session_state.get("page") == "forgot":

     col1, col2, col3 = st.columns([1,2,1])

     with col2:
        st.title("Forgot Password")

        email = st.text_input("Enter your registered email")

        if st.button("Send OTP"):

            user = users_collection.find_one({"email": email})

            if not user:
                st.error("Email not found")
            else:
                otp = generate_otp()
                st.session_state.otp = otp
                st.session_state.reset_email = email

                send_otp_email(email, otp)
                st.success("OTP sent to your email ✅")

        if st.session_state.otp:

            entered_otp = st.text_input("Enter OTP")

            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Reset Password"):

                if entered_otp != st.session_state.otp:
                    st.error("Invalid OTP")

                elif new_password != confirm_password:
                    st.error("Passwords do not match")

                else:
                    users_collection.update_one(
                        {"email": st.session_state.reset_email},
                        {"$set": {"password": new_password}}
                    )

                    st.success("Password updated successfully 🎉")

        if st.button("Back to Login"):
            switch("login")