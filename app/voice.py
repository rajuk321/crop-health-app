import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import requests
import json

# Gemini API
# genai.configure(api_key="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")

# model = genai.GenerativeModel("google/gemma-3-4b-it:free")

    
engine = pyttsx3.init()


def speak(text):

    engine = pyttsx3.init()

    engine.say(text)

    engine.runAndWait()

    engine.stop()

def listen():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        st.write("🎤 बोलिए...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="hi-IN")
        st.write("आपने कहा:", text)
        return text

    except:
        st.write("समझ नहीं आया")
        return ""

def ai_answer(question):

    # response = model.generate_content(question)
    url="https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
    }
    data = {
                "model": "google/gemma-3-4b-it:free",
                "messages": [
                    {"role": "user", "content": f"{question}"}
                ],
                "stream": False
            }
    
    response = requests.post(
        url=url,
        headers=headers,
        json=data
    )
    result = response.json()
    print(result)

    if "choices" in result:
        answer = result["choices"][0]["message"]["content"]
    else:
        answer = "AI response नहीं मिला"

    return answer

    st.title("🎤 AI Voice Assistant")

    if st.button("Speak"):

     question = listen()

    if question:

        answer = ai_answer(question)

        st.success(answer)

        speak(answer)