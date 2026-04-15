import streamlit as st
import requests

def show_weather():

    st.subheader("🌦 Weather Information")

    # 👇 INPUT FIRST (IMPORTANT)
    city = st.text_input("Enter City Name", placeholder="Enter city name")

    if st.button("Get Weather"):

        if city:   # 👈 check karo empty na ho

            API_KEY = "f28cc354391f287eb2317f34a2ea0ac6"

            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

            try:
                response = requests.get(url)
                data = response.json()

                if data["cod"] == 200:

                    temp = data["main"]["temp"]
                    humidity = data["main"]["humidity"]
                    weather = data["weather"][0]["description"]
                    rain = data.get("rain", {}).get("1h", 0)

                    st.success(f"📍 City: {city}")
                    st.write(f"🌡 Temperature: {temp} °C")
                    st.write(f"💧 Humidity: {humidity}%")
                    st.write(f"☁ Condition: {weather}")
                    st.write(f"🌧 Rain (last 1h): {rain} mm")

                else:
                    st.error("City not found")

            except:
                st.error("Weather API error")

        else:
            st.warning("Please enter city name")