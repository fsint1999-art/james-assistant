"""Clima via Open-Meteo (única chamada online; usa cache se estiver offline)."""
import time, httpx
from tools.config import cfg
_c = {"t": 0, "d": None}
WMO = {0: "céu limpo", 1: "quase limpo", 2: "parcialmente nublado", 3: "nublado", 45: "neblina", 48: "neblina", 51: "garoa", 53: "garoa", 55: "garoa forte",
       61: "chuva fraca", 63: "chuva", 65: "chuva forte", 80: "pancadas", 81: "pancadas", 82: "pancadas fortes", 95: "tempestade", 96: "tempestade", 99: "tempestade"}
def current():
    if _c["d"] and time.time() - _c["t"] < 600: return _c["d"]
    c = cfg()
    try:
        j = httpx.get("https://api.open-meteo.com/v1/forecast", timeout=6, params={
            "latitude": c["lat"], "longitude": c["lon"], "timezone": "auto", "forecast_days": 2,
            "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max"}).json()
        k, d = j["current"], j["daily"]
        _c.update(t=time.time(), d={"temp": k["temperature_2m"], "desc": WMO.get(k["weather_code"], "—"), "wind": k["wind_speed_10m"], "humidity": k["relative_humidity_2m"],
            "days": [{"min": d["temperature_2m_min"][i], "max": d["temperature_2m_max"][i], "rain": d["precipitation_probability_max"][i]} for i in (0, 1)]})
    except Exception as e:
        if not _c["d"]: return {"error": f"clima indisponível offline ({type(e).__name__})"}
    return _c["d"]
