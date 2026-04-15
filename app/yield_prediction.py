import streamlit as st
import pickle

model = pickle.load(open("yield_model.pkl","rb"))

def predict_yield():

    st.subheader("AI Yield Prediction")

    rainfall = st.number_input("Rainfall")
    temperature = st.number_input("Temperature")
    fertilizer = st.number_input("Fertilizer")

    if st.button("Predict Yield"):

        data = [[rainfall,temperature,fertilizer]]

        prediction = model.predict(data)[0]

        st.success(f"Predicted Yield: {prediction:.2f} ton/hectare")