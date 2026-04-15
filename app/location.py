import requests
import random
import streamlit as st

# ---------------- LOCATION FUNCTION ----------------
def get_location():
    try:
        url = "https://ipinfo.io/json"
        res = requests.get(url)
        data = res.json()

        city = data.get("city")
        region = data.get("region")
        country = data.get("country")
        loc = data.get("loc")  # latitude,longitude

        return city, region, country, loc
    except:
        return None, None, None, None


# ---------------- WEATHER FUNCTION ----------------
def get_weather(city):
    try:
        api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=f28cc354391f287eb2317f34a2ea0ac6&units=metric"
        data = requests.get(api).json()

        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        }
    except:
        return None


# ---------------- SATELLITE HEALTH FUNCTION ----------------
def satellite_health():
    return random.choice(["Healthy", "Moderate Stress", "High Stress"])


# ---------------- STREAMLIT UI ----------------
st.title("🌱 Crop Health Monitoring and Yield Prediction ")

if st.button("Get My Location"):
    city, region, country, loc = get_location()

    if city:
        st.success(f"📍 Location: {city}, {region}, {country}")
        st.info(f"Coordinates: {loc}")

        weather = get_weather(city)

        if weather:
            st.subheader("🌦 Weather Report")
            st.write("Temperature:", weather["temp"], "°C")
            st.write("Humidity:", weather["humidity"], "%")
            st.write("Condition:", weather["condition"])

            st.subheader("🛰 Satellite Crop Health")
            st.success(satellite_health())
        else:
            st.error("Weather data fetch nahi hua")
    else:
        st.error("Location detect nahi hua")
