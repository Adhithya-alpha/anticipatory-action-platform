import nest_asyncio
nest_asyncio.apply()
import streamlit as st
import asyncio
# --- FIX: Must happen BEFORE any other imports ---
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import streamlit as st
import ee
from google import genai
from google.genai import types
import json
import folium
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Anticipatory Action", layout="wide")

# Securely load API keys
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except FileNotFoundError:
    st.error("Missing Gemini API Key. Please add it to your secrets file.")
    st.stop()

st.title("🌪️ Cyclone Anticipatory Action Dispatcher")
st.markdown("Fusing Satellite DEM with Gemini 3.8 Flash for pre-landfall interventions.")

# Sidebar inputs
st.sidebar.header("Meteorological Inputs")
wind_speed = st.sidebar.slider("Forecasted Wind Speed (km/h)", 80, 250, 150)
surge_height = st.sidebar.slider("Storm Surge (meters)", 0.5, 5.0, 2.5)
lat, lon = 19.8, 85.8 

mock_weather_json = {
    "event": "Severe Cyclonic Storm",
    "coordinates": {"lat": lat, "lon": lon},
    "wind_speed_kmh": wind_speed,
    "storm_surge_m": surge_height,
}

# Map
st.subheader("1. Geospatial Exposure Layer")
m = folium.Map(location=[lat, lon], zoom_start=10)
folium.Circle(radius=15000, location=[lat, lon], popup="Cyclone Cone", color="red", fill=True).add_to(m)
components.html(m._repr_html_(), height=400)

# AI Reasoning
st.subheader("2. AI Reasoning & Dispatch Generation")
if st.button("Generate Anticipatory Action Plan", type="primary"):
    with st.spinner("Gemini 3.8 Flash analyzing data..."):
        prompt = f"""
        Analyze this forecast for Lat: {lat}, Lon: {lon}: {json.dumps(mock_weather_json)}
        Flooding expected up to {surge_height} meters. 
        Generate JSON with exactly three keys:
        1. "evacuation_plan": Routes and village priorities.
        2. "hardening_priorities": Infrastructure to secure.
        3. "multilingual_alert_odia": A 2-sentence public SMS alert in Odia.
        """
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            st.success("Risk Assessment Complete")
            data = json.loads(response.text)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🚨 Evacuation Plan")
                st.write(data.get("evacuation_plan", "N/A"))
                st.markdown("### 🏥 Hardening Priorities")
                st.write(data.get("hardening_priorities", "N/A"))
            with col2:
                st.markdown("### 📲 Localized Alert (Odia)")
                st.info(data.get("multilingual_alert_odia", "N/A"))
        except Exception as e:
            st.error(f"API Error: {e}")
