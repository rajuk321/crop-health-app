import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image

# Load Model
model = tf.keras.models.load_model("models/disease_model.h5")

# Class Names (training से match होना चाहिए)
class_names = [
    'Potato___Early_blight',
    'Potato___healthy',
    'Tomato___Early_blight',
    'Tomato___healthy',
    'Tomato___Late_blight'
]

# Medicine Dictionary
medicine_dict = {
    "Early_blight": "Use Mancozeb spray",
    "Late_blight": "Use Chlorothalonil spray",
    "healthy": "No medicine needed"
}

st.title("🌿 Leaf Disease Detection")

file = st.file_uploader("Upload Leaf Image", type=["jpg","png"])

if file:
    img = Image.open(file).resize((128,128))   # ⚠️ size fix
    st.image(img)

    img_array = np.array(img)/255
    img_array = np.expand_dims(img_array, axis=0)

    # 👉 YAHI PAR NEW CODE
    pred = model.predict(img_array)
    class_idx = np.argmax(pred)
    confidence = np.max(pred) * 100

    if confidence < 80:
        st.warning("⚠️ Model not confident - Try clearer image")
        st.stop()

    class_name = class_names[class_idx]

    # Split
    parts = class_name.split("___")
    leaf = parts[0]
    disease = parts[1]

    medicine = medicine_dict.get(disease, "Consult Expert")

    st.success(f"🌿 Leaf: {leaf}")
    st.error(f"🦠 Disease: {disease}")
    st.info(f"💊 Medicine: {medicine}")