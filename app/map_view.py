# ==========================================
# map_view.py
# Handles all Folium map visualizations
# for the Live Train Tracker
# ==========================================

import folium
from folium import plugins


# ==========================================
# MAIN MAP BUILDER
# ==========================================

def create_live_train_map(train_data: dict, upcoming_predictions: list = None):
    """
    Create beautiful Folium map with live train position and route.
    
    Args:
        train_data: Parsed live train data from RailRadar API
        upcoming_predictions: List of ML predictions for upcoming stations
    
    Returns:
        Folium map object
    """
    
    route = train_data.get("route", [])
    
    if not route:
        # Return empty India map if no route data
        return _create_empty_india_map()
    
    # Get all coordinates
    coords = [(s["lat"], s["lng"]) for s in route if s.get("lat") and s.get("lng")]
    
    if not coords:
        return _create_empty_india_map()
    
    # Calculate map center (average of all coordinates)
    center_lat = sum(c[0] for c in coords) / len(coords)
    center_lng = sum(c[1] for c in coords) / len(coords)
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=6,
        tiles="OpenStreetMap",
        control_scale=True
    )
    
    # Get current position info
    current_seq = train_data.get("current_sequence", 1)
    current_delay = train_data.get("current_delay", 0)
    
    # Separate route into passed and upcoming
    passed_stations = []
    upcoming_stations = []
    current_station = None
    
    for station in route:
        if not station.get("lat") or not station.get("lng"):
            continue
        
        seq = station.get("sequence", 0)
        
        if seq < current_seq:
            passed_stations.append(station)
        elif seq == current_seq:
            current_station = station
            passed_stations.append(station)  # Include current in passed line
        else:
            upcoming_stations.append(station)
    
    # ---------- Draw Route Lines ----------
    
    # Passed route (Green - completed)
    if len(passed_stations) >= 2:
        passed_coords = [
            (s["lat"], s["lng"]) 
            for s in passed_stations 
            if s.get("lat") and s.get("lng")
        ]
        folium.PolyLine(
            locations=passed_coords,
            color="#27AE60",  # Green
            weight=5,
            opacity=0.8,
            popup="✅ Journey covered",
            tooltip="Passed route"
        ).add_to(m)
    
    # Upcoming route (Red - remaining)
    if current_station and upcoming_stations:
        upcoming_line = [(current_station["lat"], current_station["lng"])]
        upcoming_line.extend([
            (s["lat"], s["lng"]) 
            for s in upcoming_stations 
            if s.get("lat") and s.get("lng")
        ])
        
        folium.PolyLine(
            locations=upcoming_line,
            color="#E74C3C",  # Red
            weight=4,
            opacity=0.7,
            dash_array="10, 10",  # Dashed line
            popup="🔮 Upcoming route",
            tooltip="Remaining route"
        ).add_to(m)
    
    # ---------- Add Station Markers ----------
    
    # Passed stations (green circles)
    for station in passed_stations[:-1]:  # Exclude current
        if not station.get("lat") or not station.get("lng"):
            continue
        
        popup_html = _create_station_popup(station, status="passed")
        
        folium.CircleMarker(
            location=[station["lat"], station["lng"]],
            radius=6,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"✅ {station.get('stationName', 'Station')}",
            color="#27AE60",
            fill=True,
            fillColor="#27AE60",
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Upcoming stations (blue circles)
    predictions_map = {}
    if upcoming_predictions:
        predictions_map = {p["station_code"]: p for p in upcoming_predictions}
    
    for station in upcoming_stations:
        if not station.get("lat") or not station.get("lng"):
            continue
        
        station_code = station.get("stationCode", "")
        prediction = predictions_map.get(station_code)
        
        popup_html = _create_station_popup(
            station, 
            status="upcoming", 
            prediction=prediction
        )
        
        folium.CircleMarker(
            location=[station["lat"], station["lng"]],
            radius=5,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"🔮 {station.get('stationName', 'Station')}",
            color="#3498DB",
            fill=True,
            fillColor="#3498DB",
            fillOpacity=0.5,
            weight=2
        ).add_to(m)
    
    # ---------- LIVE TRAIN MARKER (The Star!) ----------
    
    if current_station:
        current_lat = current_station["lat"]
        current_lng = current_station["lng"]
        
        # Create custom HTML popup for train
        train_popup_html = f"""
        <div style="font-family: Arial; min-width: 220px;">
            <h4 style="margin: 0 0 10px 0; color: #E74C3C;">
                🚂 {train_data.get('train_name', 'Train')}
            </h4>
            <table style="width: 100%; font-size: 12px;">
                <tr>
                    <td><b>Status:</b></td>
                    <td>🔴 LIVE</td>
                </tr>
                <tr>
                    <td><b>At Station:</b></td>
                    <td>{current_station.get('stationName', '')}</td>
                </tr>
                <tr>
                    <td><b>Current Delay:</b></td>
                    <td style="color: {'red' if current_delay > 30 else 'orange' if current_delay > 10 else 'green'};">
                        <b>{current_delay} minutes</b>
                    </td>
                </tr>
                <tr>
                    <td><b>Speed:</b></td>
                    <td>{train_data.get('current_speed', 0)} km/h</td>
                </tr>
                <tr>
                    <td><b>Next Stop:</b></td>
                    <td>{train_data.get('next_halt_name', 'N/A')}</td>
                </tr>
                <tr>
                    <td><b>Distance to Next:</b></td>
                    <td>{train_data.get('next_halt_distance', 0)} km</td>
                </tr>
            </table>
        </div>
        """
        
        # Pulsing train marker
        train_icon = folium.DivIcon(
            html=f"""
            <div style="
                background: linear-gradient(135deg, #E74C3C, #C0392B);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: 4px solid white;
                box-shadow: 0 0 20px rgba(231, 76, 60, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                animation: pulse 1.5s infinite;
            ">
                🚂
            </div>
            <style>
                @keyframes pulse {{
                    0% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }}
                    70% {{ box-shadow: 0 0 0 20px rgba(231, 76, 60, 0); }}
                    100% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }}
                }}
            </style>
            """,
            icon_size=(40, 40),
            icon_anchor=(20, 20)
        )
        
        folium.Marker(
            location=[current_lat, current_lng],
            popup=folium.Popup(train_popup_html, max_width=300),
            tooltip=f"🚂 LIVE: {train_data.get('train_name', 'Train')} • Delay: {current_delay} min",
            icon=train_icon
        ).add_to(m)
        
        # Add a pulsing circle around train
        folium.Circle(
            location=[current_lat, current_lng],
            radius=15000,  # 15 km
            color="#E74C3C",
            fill=True,
            fillColor="#E74C3C",
            fillOpacity=0.1,
            weight=2,
            popup="🔴 Live tracking zone"
        ).add_to(m)
    
    # ---------- Add Legend ----------
    
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 30px; 
        left: 30px; 
        z-index: 1000;
        background: white;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        font-family: Arial;
        font-size: 12px;
    ">
        <b style="font-size: 13px;">📍 Map Legend</b>
        <hr style="margin: 5px 0;">
        <div>🟢 <b>Green line:</b> Journey covered</div>
        <div>🔴 <b>Red dashed:</b> Upcoming route</div>
        <div>🚂 <b>Red marker:</b> Live train position</div>
        <div>🟢 <b>Green dots:</b> Passed stations</div>
        <div>🔵 <b>Blue dots:</b> Upcoming stations</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # ---------- Add Fullscreen Button ----------
    plugins.Fullscreen(
        position="topright",
        title="Expand map",
        title_cancel="Exit fullscreen"
    ).add_to(m)
    
    # ---------- Fit Bounds to Show All Stations ----------
    if coords:
        m.fit_bounds([
            [min(c[0] for c in coords), min(c[1] for c in coords)],
            [max(c[0] for c in coords), max(c[1] for c in coords)]
        ], padding=(30, 30))
    
    return m


# ==========================================
# HELPER: Station Popup HTML
# ==========================================

def _create_station_popup(station: dict, status: str, prediction: dict = None) -> str:
    """Create HTML popup for a station marker."""
    
    name = station.get("stationName", "Station")
    code = station.get("stationCode", "")
    
    status_icons = {
        "passed": "✅",
        "current": "🚂",
        "upcoming": "🔮"
    }
    icon = status_icons.get(status, "📍")
    
    status_colors = {
        "passed": "#27AE60",
        "current": "#E74C3C",
        "upcoming": "#3498DB"
    }
    color = status_colors.get(status, "#000")
    
    # Scheduled times
    sched_arr = station.get("scheduledArrival", "")
    sched_dep = station.get("scheduledDeparture", "")
    actual_arr = station.get("actualArrival", "")
    actual_dep = station.get("actualDeparture", "")
    
    # Format times (extract HH:MM)
    def fmt(t):
        if t and "T" in t:
            return t.split("T")[1][:5]
        return "—"
    
    delay_arr = station.get("delayArrival", 0) or 0
    delay_dep = station.get("delayDeparture", 0) or 0
    
    html = f"""
    <div style="font-family: Arial; min-width: 220px;">
        <h4 style="margin: 0 0 8px 0; color: {color};">
            {icon} {name}
        </h4>
        <div style="font-size: 11px; color: #888; margin-bottom: 8px;">
            Code: <b>{code}</b> | Stop #{station.get('sequence', '')}
        </div>
        <table style="width: 100%; font-size: 11px;">
            <tr>
                <td><b>Scheduled Arr:</b></td>
                <td>{fmt(sched_arr)}</td>
            </tr>
            <tr>
                <td><b>Scheduled Dep:</b></td>
                <td>{fmt(sched_dep)}</td>
            </tr>
    """
    
    if status == "passed":
        html += f"""
            <tr>
                <td><b>Actual Arr:</b></td>
                <td>{fmt(actual_arr)}</td>
            </tr>
            <tr>
                <td><b>Delay:</b></td>
                <td style="color: {'red' if delay_arr > 15 else 'orange' if delay_arr > 5 else 'green'};">
                    <b>{delay_arr} min</b>
                </td>
            </tr>
        """
    
    if status == "upcoming" and prediction:
        ml_delay = prediction.get("predicted_delay", 0)
        weather = prediction.get("weather", {})
        html += f"""
            <tr>
                <td colspan="2" style="padding-top: 8px;">
                    <hr style="margin: 4px 0;">
                    <b>🧠 ML Prediction:</b> {ml_delay:.0f} min
                </td>
            </tr>
        """
        if weather and weather.get("success"):
            html += f"""
            <tr>
                <td colspan="2">
                    <b>🌦 Weather:</b> {weather.get('icon', '')} 
                    {weather.get('temperature', '')}°C {weather.get('condition', '')}
                </td>
            </tr>
            """
    
    html += """
        </table>
    </div>
    """
    
    return html


# ==========================================
# HELPER: Empty Map (Fallback)
# ==========================================

def _create_empty_india_map():
    """Create empty India map when no data available."""
    m = folium.Map(
        location=[22.5937, 78.9629],  # Center of India
        zoom_start=5,
        tiles="OpenStreetMap"
    )
    
    folium.Marker(
        location=[22.5937, 78.9629],
        popup="No live train data available",
        tooltip="Enter a train number to track"
    ).add_to(m)
    
    return m