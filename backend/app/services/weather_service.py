import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude: float, longitude: float):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "hourly": "rain",
        "forecast_days": 1,
        "timezone": "auto"
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    current = data.get("current", {})

    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind_speed = current.get("wind_speed_10m")

    hourly = data.get("hourly", {})
    rain_values = hourly.get("rain", [])

    rainfall = sum(
        value for value in rain_values
        if value is not None
    )

    return {
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "rainfall": rainfall
    }