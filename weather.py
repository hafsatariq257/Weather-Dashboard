import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# --- UI THEMING & GLASSMORPHISM CSS ---
st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Background Image and Main Theme */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=2000');
        background-size: cover;
        color: white;
    }
    
    /* Glassmorphism Card Style */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    /* Input field styling */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    h1, h2, h3, p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- START YOUR ORIGINAL LOGIC ---

st.title("🌦️ Weather Dashboard")

city = st.text_input("Enter city name")

if city.strip() == "":
    st.markdown('<div class="glass-card">👆 Please enter a city name</div>', unsafe_allow_html=True)
    st.stop()

geo_url = (
    f"https://api.openweathermap.org/geo/1.0/direct"
    f"?q={city}&limit=1&appid={API_KEY}"
)

geo_resp = requests.get(geo_url).json()

if not isinstance(geo_resp, list) or len(geo_resp) == 0:
    st.error("City not found or API error")
    st.write("API response:", geo_resp)
    st.stop()

lat = geo_resp[0]["lat"]
lon = geo_resp[0]["lon"]

weather_url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
)

weather = requests.get(weather_url).json()

if weather.get("cod") != 200:
    st.error("⚠️ Weather API error")
    st.write(weather)
    st.stop()

# --- STYLED OUTPUT: Current Weather ---
st.markdown(f"""
    <div class="glass-card">
        <h3>🌤 Current Weather in {city.title()}</h3>
        <h1 style="font-size: 50px; margin: 0;">{weather['main']['temp']} °C</h1>
        <p style="font-size: 18px; opacity: 0.8;">{weather['weather'][0]['description'].title()}</p>
        <hr style="opacity: 0.2;">
        <p>💧 Humidity: {weather['main']['humidity']}%</p>
    </div>
    """, unsafe_allow_html=True)

forecast_url = (
    f"https://api.openweathermap.org/data/2.5/forecast"
    f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
)

forecast = requests.get(forecast_url).json()

if forecast.get("cod") != "200":
    st.error("⚠️ Forecast API error")
    st.write(forecast)
    st.stop()

df = pd.DataFrame(forecast["list"])
df["date"] = pd.to_datetime(df["dt_txt"])
df["temp"] = df["main"].apply(lambda x: x["temp"])

# --- STYLED OUTPUT: Forecast Chart ---
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("📈 Temperature Forecast")

fig = px.line(
    df,
    x="date",
    y="temp",
    title="Temperature Forecast (Next 5 Days)"
)

# Dark theme for the chart
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color="white",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)