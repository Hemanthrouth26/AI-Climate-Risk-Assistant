import streamlit as st
import requests

st.set_page_config(page_title="AI Climate Risk Assistant", layout="centered")

st.title("🌍 AI Climate Risk Assistant")
st.write("Enter location details to assess climate risks.")

# Inputs
lat = st.text_input("Latitude", "12.9")
lon = st.text_input("Longitude", "77.5")

# User type selection
user_type = st.selectbox(
    "Select User Type",
    ["urban", "farmer", "student", "hospital"]
)

if st.button("Get Risk Report"):
    payload = {
        "lat": float(lat),
        "lon": float(lon),
        "user_type": user_type
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/risk_report",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            # 📊 Overall Risk
            st.subheader("📊 Overall Climate Risk")
            st.write(f"Risk Level: {data['risk_level']}")
            st.write(f"Risk Score: {data['risk_score']} / 10")

            # 📌 Breakdown
            st.subheader("📌 Risk Breakdown")
            st.json(data["risk_breakdown"])

            # 🧠 Explainability
            st.subheader("🧠 Why is this risk level?")
            for reason in data["explanation"]:
                st.write("•", reason)

            # 🏘 Community Comparison (NEW)
            st.subheader("🏘 Community Risk Comparison")
            st.write(f"Your Risk Score: {data['community_comparison']['your_risk']}")
            st.write(f"Nearby Average Risk: {data['community_comparison']['nearby_average_risk']}")
            st.success(data['community_comparison']['status'])

            # 🌡 Temperature
            st.subheader("🌡 Temperature")
            st.write(f"{data['temperature']} °C")

            # 🌫 AQI
            st.subheader("🌫 Air Quality Index")
            st.write(data["aqi"])

            # 🤖 Recommendations
            st.subheader("🤖 AI Safety Recommendations")
            for rec in data["recommendations"]:
                st.write("•", rec)

        else:
            st.error("Backend error occurred")

    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
