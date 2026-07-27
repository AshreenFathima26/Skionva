import requests

API_KEY = "b75be722883447d8a24172227262707"

BASE_URL = "http://api.weatherapi.com/v1/current.json"

def get_weather(lat, lon):
    try:
        response = requests.get(
            BASE_URL,
            params={
                "key": API_KEY,
                "q": f"{lat},{lon}",
                "aqi": "yes"
            }
        )

        response.raise_for_status()
        data = response.json()
        print(data)   # Temporary, for testing

        return {
            "city": data["location"]["name"],
            "temperature": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "icon": "https:" + data["current"]["condition"]["icon"],
            "humidity": data["current"]["humidity"],
            "uv": data["current"]["uv"],
            "wind": data["current"]["wind_kph"]
        }

    except Exception as e:
        print("Weather Error:", e)
        return None