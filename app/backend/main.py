from fastapi import FastAPI
from pydantic import BaseModel

from app.backend.weather import fetch_weather, fetch_aqi
from app.backend.rag import retrieve

app = FastAPI(title="AI Climate Risk Assistant")


# ------------------ Data Model ------------------
class Location(BaseModel):
    lat: float
    lon: float
    user_type: str


# ------------------ Helper Functions ------------------
def calculate_risk_score(lat, lon, user_type):
    weather = fetch_weather(lat, lon)
    aqi = fetch_aqi(lat, lon)

    temp = weather["main"]["temp"]
    rain = weather.get("rain", {}).get("1h", 0)
    aqi_index = aqi["list"][0]["main"]["aqi"]

    heat_score = 4 if temp >= 40 else 3 if temp >= 35 else 2 if temp >= 30 else 1
    flood_score = 4 if rain >= 30 else 3 if rain >= 20 else 2 if rain >= 10 else 1
    air_score = 4 if aqi_index >= 5 else 3 if aqi_index >= 4 else 2 if aqi_index >= 3 else 1

    vulnerability = {
        "urban": 1.0,
        "farmer": 1.2,
        "student": 1.1,
        "hospital": 1.3
    }.get(user_type, 1.0)

    return int((heat_score + flood_score + air_score) * vulnerability)


def format_recommendations(docs):
    """
    Clean and format RAG responses into readable bullet points
    and remove broken/incomplete sentences.
    """
    clean_recs = []

    for text, _ in docs:
        lines = text.split("\n")
        for line in lines:
            line = line.strip()

            # Skip section headers
            if line.endswith(":"):
                continue

            # Remove bullets and dashes
            line = line.lstrip("-• ").strip()

            # Skip short or broken lines
            if len(line) < 20:
                continue

            # Skip unfinished sentences
            if not line.endswith((".", "!", "?")):
                continue

            clean_recs.append(line)

    # Remove duplicates but preserve order
    seen = set()
    final = []
    for rec in clean_recs:
        if rec not in seen:
            final.append(rec)
            seen.add(rec)

    return final


# ------------------ API Route ------------------
@app.post("/risk_report")
def risk_report(loc: Location):
    weather = fetch_weather(loc.lat, loc.lon)
    aqi = fetch_aqi(loc.lat, loc.lon)

    temp = weather["main"]["temp"]
    rain = weather.get("rain", {}).get("1h", 0)
    aqi_index = aqi["list"][0]["main"]["aqi"]

    # -------- MULTI FACTOR RISK SCORING --------
    heat_score = 4 if temp >= 40 else 3 if temp >= 35 else 2 if temp >= 30 else 1
    flood_score = 4 if rain >= 30 else 3 if rain >= 20 else 2 if rain >= 10 else 1
    air_score = 4 if aqi_index >= 5 else 3 if aqi_index >= 4 else 2 if aqi_index >= 3 else 1

    vulnerability = {
        "urban": 1.0,
        "farmer": 1.2,
        "student": 1.1,
        "hospital": 1.3
    }.get(loc.user_type, 1.0)

    total_risk_score = int((heat_score + flood_score + air_score) * vulnerability)

    if total_risk_score >= 9:
        risk_level = "High"
    elif total_risk_score >= 5:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    # -------- EXPLANATION LAYER --------
    explanation = []

    if heat_score >= 3:
        explanation.append("High temperature levels increase heat stress risk.")
    if flood_score >= 3:
        explanation.append("Heavy rainfall increases chances of flooding.")
    if air_score >= 3:
        explanation.append("Poor air quality can cause respiratory problems.")

    if loc.user_type == "farmer":
        explanation.append("Farmers are vulnerable to climate changes affecting crops.")
    elif loc.user_type == "student":
        explanation.append("Students are sensitive to heat and air pollution exposure.")
    elif loc.user_type == "hospital":
        explanation.append("Hospitals require stable environmental conditions for patient safety.")
    elif loc.user_type == "urban":
        explanation.append("Urban areas have slower drainage which increases flood risk.")

    # -------- COMMUNITY RISK COMPARISON --------
    nearby_points = [
        (loc.lat + 0.05, loc.lon),
        (loc.lat - 0.05, loc.lon),
        (loc.lat, loc.lon + 0.05),
        (loc.lat, loc.lon - 0.05),
    ]

    nearby_scores = []
    for lat, lon in nearby_points:
        score = calculate_risk_score(lat, lon, loc.user_type)
        nearby_scores.append(score)

    avg_nearby_risk = round(sum(nearby_scores) / len(nearby_scores), 2)

    if total_risk_score > avg_nearby_risk:
        community_status = "Your area is at higher risk than nearby regions."
    elif total_risk_score < avg_nearby_risk:
        community_status = "Your area is safer compared to nearby regions."
    else:
        community_status = "Your area has similar risk to nearby regions."

    # -------- ROLE-SPECIFIC DYNAMIC RAG QUERIES --------
    rag_queries = []

    # Heat
    if heat_score >= 3:
        if loc.user_type == "farmer":
            rag_queries.append("heatwave protection techniques for crops and farmers")
        elif loc.user_type == "student":
            rag_queries.append("student safety guidelines during heatwaves")
        elif loc.user_type == "hospital":
            rag_queries.append("hospital heatwave emergency response protocol")
        else:
            rag_queries.append("heatwave safety tips for urban residents")

    # Flood
    if flood_score >= 3:
        if loc.user_type == "farmer":
            rag_queries.append("flood protection measures for crops and agricultural land")
        elif loc.user_type == "student":
            rag_queries.append("student safety during floods and heavy rainfall")
        elif loc.user_type == "hospital":
            rag_queries.append("hospital flood emergency preparedness plan")
        else:
            rag_queries.append("urban flood preparedness and evacuation safety")

    # Air Quality
    if air_score >= 3:
        if loc.user_type == "farmer":
            rag_queries.append("air pollution impact on crops and farmer health safety")
        elif loc.user_type == "student":
            rag_queries.append("student health protection during air pollution")
        elif loc.user_type == "hospital":
            rag_queries.append("hospital air quality management and patient protection")
        else:
            rag_queries.append("urban air pollution health protection measures")

    # Fallback
    if not rag_queries:
        if loc.user_type == "farmer":
            rag_queries.append("general climate safety and sustainable farming practices")
        elif loc.user_type == "student":
            rag_queries.append("general climate awareness and student safety measures")
        elif loc.user_type == "hospital":
            rag_queries.append("general hospital disaster preparedness guidelines")
        else:
            rag_queries.append("general urban climate safety and preparedness tips")

    # -------- FETCH DOCUMENTS --------
    docs = []
    seen_texts = set()

    for q in rag_queries:
        results = retrieve(q, top_k=1)
        for text, meta in results:
            if text not in seen_texts:
                docs.append((text, meta))
                seen_texts.add(text)

    # -------- FINAL RESPONSE --------
    return {
        "location": {"lat": loc.lat, "lon": loc.lon},
        "user_type": loc.user_type,
        "temperature": temp,
        "aqi": aqi_index,
        "risk_score": total_risk_score,
        "risk_level": risk_level,
        "risk_breakdown": {
            "heat": heat_score,
            "flood": flood_score,
            "air_quality": air_score
        },
        "explanation": explanation,
        "community_comparison": {
            "your_risk": total_risk_score,
            "nearby_average_risk": avg_nearby_risk,
            "status": community_status
        },
        "recommendations": format_recommendations(docs),
        "sources": [m["source"] for _, m in docs]
    }
