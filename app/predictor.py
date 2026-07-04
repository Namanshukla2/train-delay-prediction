# ==========================================
# predictor.py
# Loads trained ML model and provides
# a clean prediction function for the app.
# ==========================================

import os
import joblib
import pandas as pd


# ---------- Load All Model Assets ----------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
encoders = joblib.load(os.path.join(MODEL_DIR, "encoders.pkl"))
feature_cols = joblib.load(os.path.join(MODEL_DIR, "features.pkl"))
lookup = joblib.load(os.path.join(MODEL_DIR, "lookup_tables.pkl"))

train_avg = lookup["train_avg"]
station_avg = lookup["station_avg"]
train_station_avg = lookup["train_station_avg"]
zone_avg = lookup["zone_avg"]
late_ratio = lookup["late_ratio"]
route_features = lookup["route_features"]


# ---------- Helper: Season Mapping ----------

def get_season(month):
    """Return season name based on month number."""
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Post-Monsoon"


# ---------- Main Prediction Function ----------

def predict_delay(train_no, station_name, station_no,
                  station_zone, type_code,
                  month, day, day_of_week):
    """
    Predict train delay in minutes based on user inputs.
    Returns dictionary with prediction + supporting details.
    """

    # Train average delay
    t_avg = train_avg.loc[train_avg["train_no"] == train_no, "train_avg_delay"]
    t_avg_val = t_avg.iloc[0] if not t_avg.empty else train_avg["train_avg_delay"].mean()

    # Station average delay
    s_avg = station_avg.loc[station_avg["station_name"] == station_name, "station_avg_delay"]
    s_avg_val = s_avg.iloc[0] if not s_avg.empty else station_avg["station_avg_delay"].mean()

    # Train + Station combined average
    ts_avg = train_station_avg.loc[
        (train_station_avg["train_no"] == train_no) &
        (train_station_avg["station_name"] == station_name),
        "train_station_avg_delay"
    ]
    ts_avg_val = ts_avg.iloc[0] if not ts_avg.empty else t_avg_val

    # Zone average
    z_avg = zone_avg.loc[zone_avg["station_zone"] == station_zone, "zone_avg_delay"]
    z_avg_val = z_avg.iloc[0] if not z_avg.empty else zone_avg["zone_avg_delay"].mean()

    # Late ratio
    lr = late_ratio.loc[late_ratio["train_no"] == train_no, "late_ratio"]
    lr_val = lr.iloc[0] if not lr.empty else late_ratio["late_ratio"].mean()

    # Route features
    rf = route_features.loc[route_features["train_no"] == train_no]
    if not rf.empty:
        total_distance = rf["total_route_distance"].iloc[0]
        total_stops = rf["total_stops"].iloc[0]
    else:
        total_distance = route_features["total_route_distance"].median()
        total_stops = route_features["total_stops"].median()

    # Approximate distance from origin
    distance_from_origin = (station_no / max(total_stops, 1)) * total_distance

    # ---------- Encode categorical inputs ----------

    if type_code in encoders["type_code"].classes_:
        type_code_enc = encoders["type_code"].transform([type_code])[0]
    else:
        type_code_enc = 0

    if station_zone in encoders["station_zone"].classes_:
        station_zone_enc = encoders["station_zone"].transform([station_zone])[0]
    else:
        station_zone_enc = 0

    season_str = get_season(month)
    if season_str in encoders["season"].classes_:
        season_enc = encoders["season"].transform([season_str])[0]
    else:
        season_enc = 0

    # ---------- Build Feature Vector ----------

    feature_dict = {
        "month": month,
        "day": day,
        "day_of_week": day_of_week,
        "station_no": station_no,
        "distance_from_origin": distance_from_origin,
        "total_route_distance": total_distance,
        "total_stops": total_stops,
        "train_avg_delay": t_avg_val,
        "station_avg_delay": s_avg_val,
        "train_station_avg_delay": ts_avg_val,
        "zone_avg_delay": z_avg_val,
        "late_ratio": lr_val,
        "type_code": type_code_enc,
        "station_zone": station_zone_enc,
        "season": season_enc
    }

    X_input = pd.DataFrame([feature_dict])[feature_cols]

    predicted_delay = float(model.predict(X_input)[0])

    return {
        "predicted_delay_min": round(predicted_delay, 2),
        "season": season_str,
        "train_avg_delay": round(t_avg_val, 2),
        "station_avg_delay": round(s_avg_val, 2),
        "route_distance_km": round(total_distance, 2),
        "total_stops": int(total_stops)
    }