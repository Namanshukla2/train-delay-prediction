# ==========================================
# api_client.py
# Handles all external API calls
# (RailRadar, OpenWeatherMap)
# ==========================================

import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
RAILRADAR_API_KEY = os.getenv("RAILRADAR_API_KEY", "")

# Base URLs
RAILRADAR_BASE_URL = "https://api.railradar.in/v1"


# ==========================================
# RAILRADAR API - Live Train Tracking
# ==========================================

@st.cache_data(ttl=60, show_spinner=False)
def get_live_train_status(train_number: str, include_coordinates: bool = True) -> dict:
    """
    Fetch live train status from RailRadar API.
    Cache: 60 seconds
    """
    
    fallback = {
        "success": False,
        "error": "API unavailable",
        "data": None
    }
    
    if not RAILRADAR_API_KEY:
        fallback["error"] = "API key not configured"
        return fallback
    
    try:
        url = f"{RAILRADAR_BASE_URL}/trains/{train_number}/live"
        
        headers = {
            "Authorization": f"Bearer {RAILRADAR_API_KEY}"
        }
        
        params = {
            "includeCoordinates": "true" if include_coordinates else "false"
        }
        
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return {
                    "success": True,
                    "data": data.get("data"),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unknown error"),
                    "data": None
                }
        
        elif response.status_code == 401:
            return {
                "success": False,
                "error": "Invalid API key",
                "data": None
            }
        
        elif response.status_code == 429:
            return {
                "success": False,
                "error": "Rate limit exceeded. Try again in a minute.",
                "data": None
            }
        
        elif response.status_code == 404:
            return {
                "success": False,
                "error": f"Train {train_number} not found or not running today",
                "data": None
            }
        
        else:
            return {
                "success": False,
                "error": f"API error: {response.status_code}",
                "data": None
            }
    
    except requests.Timeout:
        return {
            "success": False,
            "error": "API request timeout",
            "data": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}",
            "data": None
        }


@st.cache_data(ttl=300, show_spinner=False)
def get_train_details(train_number: str) -> dict:
    """
    Fetch static train details.
    Cache: 5 minutes
    """
    if not RAILRADAR_API_KEY:
        return {"success": False, "data": None}
    
    try:
        url = f"{RAILRADAR_BASE_URL}/trains/{train_number}"
        headers = {"Authorization": f"Bearer {RAILRADAR_API_KEY}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return {"success": False, "data": None}
    
    except Exception:
        return {"success": False, "data": None}


# ==========================================
# HELPER: Parse Live Train Data
# ==========================================

def parse_live_train_data(api_response: dict) -> dict:
    """
    Parse RailRadar API response into clean format for UI.
    """
    if not api_response.get("success") or not api_response.get("data"):
        return None
    
    data = api_response["data"]
    train = data.get("train", {})
    current_loc = data.get("currentLocation", {})
    next_halt = data.get("nextHalt", {})
    previous_halt = data.get("previousHalt", {})
    route = data.get("route", [])
    exceptions = data.get("exceptions", [])
    
    return {
        # Train info
        "train_number": data.get("trainNumber"),
        "train_name": data.get("trainName"),
        "status": data.get("status", "unknown"),
        "is_live": data.get("isLive", False),
        "current_delay": data.get("delayMinutes", 0),
        "last_updated": data.get("lastUpdatedAt"),
        "start_date": data.get("startDate"),
        
        # Train metadata
        "train_type": train.get("type", "Unknown"),
        "source_station": train.get("source", {}).get("name", ""),
        "source_code": train.get("source", {}).get("code", ""),
        "destination_station": train.get("destination", {}).get("name", ""),
        "destination_code": train.get("destination", {}).get("code", ""),
        "total_distance": train.get("distance", 0),
        "avg_speed": train.get("avgSpeed", 0),
        "max_speed": train.get("maxSpeed", 0),
        "total_halts": train.get("totalHalts", 0),
        
        # Current position
        "current_station_code": current_loc.get("stationCode"),
        "current_sequence": current_loc.get("sequence", 1),
        "current_status": current_loc.get("status", "unknown"),
        "current_speed": current_loc.get("speedKmh", 0),
        "segment_progress": current_loc.get("segmentProgress", 0),
        "is_actual_position": current_loc.get("isActualPosition", False),
        
        # Next & Previous halts
        "previous_halt_name": previous_halt.get("stationName", ""),
        "previous_halt_code": previous_halt.get("stationCode", ""),
        "next_halt_name": next_halt.get("stationName", ""),
        "next_halt_code": next_halt.get("stationCode", ""),
        "next_halt_distance": next_halt.get("distance", 0),
        
        # Route with coordinates
        "route": route,
        
        # Exceptions
        "exceptions": exceptions,
        "has_exceptions": len(exceptions) > 0
    }


# ==========================================
# WEATHER API - OpenWeatherMap
# ==========================================

def clean_city_name(station_full_name: str) -> str:
    """Extract proper city name from railway station name."""
    if not station_full_name:
        return "Delhi"
    
    name = str(station_full_name).strip().upper()
    
    prefixes_to_remove = [
        'V ', 'NEW ', 'OLD ', 'PT ', 'SMT ', 'DR ', 'SR ',
        'HAZRAT ', 'MAHAVEER ', 'SHRI ', 'SHREE ',
        'CHHATRAPATI SHIVAJI MAHARAJ ', 'CHHATRAPATI '
    ]
    
    suffixes_to_remove = [
        ' JN', ' JUNCTION', ' CANTT', ' CANTONMENT',
        ' TERMINUS', ' TERMINAL', ' CENTRAL',
        ' HALT', ' CITY', ' STATION',
        ' ROAD', ' RD', ' TMS', ' TERM'
    ]
    
    changed = True
    while changed:
        changed = False
        for prefix in prefixes_to_remove:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
                changed = True
                break
    
    changed = True
    while changed:
        changed = False
        for suffix in suffixes_to_remove:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
                changed = True
                break
    
    words = name.split()
    if len(words) > 2:
        name = words[-1]
    elif len(words) == 2:
        name = words[-1]
    
    return name.title() if name else "Delhi"


@st.cache_data(ttl=1800, show_spinner=False)
def get_weather_by_city(city_name: str) -> dict:
    """
    Get current weather for a city.
    Cache: 30 minutes (weather doesn't change fast)
    """
    
    fallback = {
        "success": False,
        "temperature": 25,
        "condition": "Clear",
        "description": "Weather data unavailable",
        "humidity": 60,
        "wind_speed": 5,
        "icon": "🌤️",
        "delay_risk": "low",
        "city_used": city_name
    }
    
    if not OPENWEATHER_API_KEY:
        return fallback
    
    cleaned_city = clean_city_name(city_name)
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{cleaned_city},IN",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            params["q"] = cleaned_city
            response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            fallback["city_used"] = cleaned_city
            return fallback
        
        data = response.json()
        
        weather_main = data["weather"][0]["main"]
        weather_desc = data["weather"][0]["description"].title()
        temperature = round(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        weather_icons = {
            "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
            "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️",
            "Mist": "🌫️", "Fog": "🌫️", "Haze": "🌫️",
            "Smoke": "🌫️", "Dust": "🌫️"
        }
        icon = weather_icons.get(weather_main, "🌤️")
        
        high_risk = ["Rain", "Thunderstorm", "Snow", "Fog", "Mist"]
        medium_risk = ["Drizzle", "Haze", "Clouds", "Smoke", "Dust"]
        
        if weather_main in high_risk:
            delay_risk = "high"
        elif weather_main in medium_risk:
            delay_risk = "medium"
        else:
            delay_risk = "low"
        
        return {
            "success": True,
            "temperature": temperature,
            "condition": weather_main,
            "description": weather_desc,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "icon": icon,
            "delay_risk": delay_risk,
            "city_used": cleaned_city
        }
    
    except Exception as e:
        print(f"Weather API error for '{city_name}' → '{cleaned_city}': {e}")
        fallback["city_used"] = cleaned_city
        return fallback


def calculate_weather_adjustment(weather_data: dict, base_delay: float) -> dict:
    """Adjust ML prediction based on weather conditions."""
    
    adjustment = 0
    reason = ""
    
    if not weather_data.get("success", False):
        return {
            "adjustment_min": 0,
            "adjusted_delay": base_delay,
            "reason": "Weather data unavailable"
        }
    
    risk = weather_data.get("delay_risk", "low")
    condition = weather_data.get("condition", "Clear")
    
    if risk == "high":
        if condition in ["Rain", "Thunderstorm"]:
            adjustment = 10
            reason = f"Heavy {condition.lower()} may cause additional delay"
        elif condition in ["Fog", "Mist"]:
            adjustment = 15
            reason = "Poor visibility due to fog may slow trains"
        elif condition == "Snow":
            adjustment = 20
            reason = "Snowfall may significantly impact train speed"
        else:
            adjustment = 8
            reason = "Adverse weather conditions"
    
    elif risk == "medium":
        adjustment = 5
        reason = f"{condition} conditions may cause minor delays"
    
    else:
        adjustment = 0
        reason = "Clear weather - no adjustment needed"
    
    return {
        "adjustment_min": adjustment,
        "adjusted_delay": base_delay + adjustment,
        "reason": reason
    }