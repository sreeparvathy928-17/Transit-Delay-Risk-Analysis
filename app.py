import streamlit as st
import pandas as pd
import pickle
import requests

# Load trained K-Means model
with open("kmeans_model.pkl", "rb") as file:
    kmeans = pickle.load(file)

# Load cluster labels
with open("cluster_labels.pkl", "rb") as file:
    labels = pickle.load(file)

# Page title
st.title("🚌 Public Transit Delay Risk Analysis")

st.write(
    "Enter your location to analyze rainfall and estimate "
    "public transit delay risk."
)

# User enters location
location = st.text_input(
    "📍 Enter Location",
    placeholder="Example: Kottayam"
)

# API key will be stored safely in Streamlit Secrets
API_KEY = st.secrets["WEATHER_API_KEY"]

if st.button("Check Delay Risk"):

    if location.strip() == "":
        st.warning("Please enter a location.")

    else:
        try:
            # Get current weather
            url = "https://api.weatherapi.com/v1/current.json"

            params = {
                "key": API_KEY,
                "q": location
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            weather = response.json()

            city = weather["location"]["name"]
            region = weather["location"]["region"]
            rainfall = weather["current"]["precip_mm"]

            # Give rainfall to K-Means model
            live_data = pd.DataFrame(
                [[rainfall]],
                columns=["Rainfall_mm"]
            )

            cluster = kmeans.predict(live_data)[0]
            category = labels[cluster]

            # Delay risk
            if category == "Low Rainfall":
                risk = "LOW"
                delay = "0–5 minutes"

            elif category == "Moderate Rainfall":
                risk = "MODERATE"
                delay = "5–15 minutes"

            else:
                risk = "HIGH"
                delay = "15–30+ minutes"

            # Display result
            st.success("Analysis Completed!")

            st.subheader(f"📍 {city}, {region}")

            st.metric(
                "🌧️ Current Rainfall",
                f"{rainfall} mm"
            )

            st.write("**Rainfall Category:**", category)
            st.write("**Transit Delay Risk:**", risk)
            st.write("**Estimated Delay Range:**", delay)

            st.caption(
                "The delay range is a rule-based estimate based on "
                "the rainfall cluster."
            )

        except Exception:
            st.error(
                "Unable to get weather information. "
                "Please check the location and try again."
            )
