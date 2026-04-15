import streamlit as st
from disease_solution import detect_disease
def dashboard():

    st.title("🌱 Crop Health Monitoring")

    st.success(f"Welcome {st.session_state.user}")

    menu = st.sidebar.selectbox(
        "Menu",
        ["Profile","Disease Detection","Yield Prediction","Weather"]
    )

    if menu == "Profile":
        st.write("Farmer Information")

    if menu == "Disease Detection":
        st.write("Upload Crop Image")
        from disease_solution import detect_disease
    if menu == "Yield Prediction":
        st.write("Yield Prediction Model")

    if menu == "Weather":
        st.write("Weather Data Here")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    elif menu == "Disease Detection":
       detect_disease()    