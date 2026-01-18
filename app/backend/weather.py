def fetch_weather(lat, lon):
    # 🔧 MOCK WEATHER DATA (API fallback)
    return {
        "name": "Bengaluru",
        "main": {
            "temp": 29.5
        },
        "weather": [
            {"description": "light rain"}
        ],
        "rain": {
            "1h": 25
        }
    }

def fetch_aqi(lat, lon):
    # 🔧 MOCK AQI DATA (API fallback)
    return {
        "list": [
            {
                "main": {
                    "aqi": 3
                }
            }
        ]
    }
