# 🚂 Train Delay Prediction System

> An industry-grade Machine Learning system that predicts Indian Railways train delays with real-time GPS tracking, weather-based intelligence, and interactive analytics — all in one dashboard.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange.svg)
![Deployed](https://img.shields.io/badge/deployed-Streamlit%20Cloud-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🌐 Live Demo

🔗 **[Try the Live App →](https://train-delay-prediction-projectbynaman.streamlit.app)**

Real-time deployed version. Powered by:
- RailRadar API (Live GPS tracking)
- OpenWeatherMap API (Weather-based prediction)
- XGBoost ML Model (Trained on 7.3M+ records)

---

## 📸 Preview

Live tracking + ML predictions + Analytics — all inside a single Streamlit application.

*(Screenshots will be added below)*

---

## ✨ Features

### 🔮 ML-Powered Delay Prediction
- Predicts train delays in minutes using XGBoost regression
- Trained on 7.3 million cleaned records from Indian Railways
- Considers train history, station patterns, zones, distance, season
- Smart searchable train + station selection

### 📈 Interactive Analytics Dashboard
- Zone-wise delay comparison across 18 Indian Railway zones
- Monthly delay trends showing seasonal patterns
- Train type comparisons (Rajdhani, Shatabdi, Superfast, Passenger)
- Top 10 most delayed trains ranked
- KPI cards + smart insights

### 🚂 Live Train Tracker
- Real-time GPS tracking via RailRadar API
- Animated halt-only journey timeline with delay color coding:
  - 🟢 On Time (0–9 min)
  - 🟡 Minor Delay (10–24 min)
  - 🔴 Major Delay (25+ min)
- ML predictions for upcoming halts
- Weather-adjusted delay forecasting via OpenWeatherMap
- Handles running, completed, cancelled, not-started trains
- Auto-scroll to current train position

### 📋 Data Explorer
- Browse and filter 100K+ delay records
- Filter by zone, train type, delay range, month
- Search by train name/number or station code/name
- Download filtered dataset as CSV

### 🎯 Smart UX
- Full station names + codes displayed
- Auto-detected zones
- Honest data presentation (5–15 min GPS lag disclaimer)
- Optimized performance (halt filtering + smart caching)
- Mobile responsive layout

---

## 🧠 Machine Learning Approach

### Dataset
- Source: Indian Railways Historical Delay Dataset (Kaggle)
- Original: 38.4 million rows
- Cleaned + Sampled: 7.3 million rows
- Coverage: 7,000+ trains • 8,000+ stations • 18 zones

### Feature Engineering
- Temporal: month, day_of_week, season
- Historical aggregates:
  - train_avg_delay
  - station_avg_delay
  - train_station_avg_delay
  - zone_avg_delay
  - late_ratio
- Route features:
  - total_route_distance
  - total_stops
  - distance_from_origin
- Categorical encoding for type & zone

### Model Performance
| Metric | Value |
|--------|-------|
| MAE | 20.57 min |
| RMSE | 40.05 min |
| R² Score | 0.5431 |

Model file: model/xgb_model.pkl

### Real-Time Intelligence Layer
- RailRadar API → Live train location + delay
- OpenWeatherMap API → Weather-based delay adjustment
- Streamlit @st.cache_data optimization:
  - Live data cache: 60 seconds
  - Weather cache: 30 minutes

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| ML Framework | XGBoost, scikit-learn |
| Data Processing | Pandas, NumPy |
| Dashboard | Streamlit |
| Charts | Plotly |
| APIs | RailRadar, OpenWeatherMap |
| Deployment | Streamlit Cloud |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

train-delay-prediction/
│
├── app/
│   ├── app.py               (Main Streamlit application)
│   ├── predictor.py         (ML model loader + prediction)
│   ├── charts.py            (Analytics chart functions)
│   ├── api_client.py        (External API integrations)
│   └── map_view.py          (Visualization helpers)
│
├── model/
│   ├── xgb_model.pkl        (Trained XGBoost model)
│   ├── encoders.pkl         (Label encoders)
│   ├── features.pkl         (Feature list)
│   ├── lookup_tables.pkl    (Historical aggregates)
│   ├── smart_lookup.pkl     (UI-friendly train/station data)
│   └── dashboard_data.pkl   (Analytics KPI data)
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   └── 02_model_training.ipynb
│
├── data/
│   └── processed/
│       └── dashboard_sample.csv
│
├── requirements.txt
├── .gitignore
└── README.md

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### 1️⃣ Clone Repository
git clone https://github.com/Namanshukla2/train-delay-prediction.git
cd train-delay-prediction

### 2️⃣ Setup Virtual Environment
python -m venv venv

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Configure API Keys
Create a .env file:

OPENWEATHER_API_KEY=your_openweather_key
RAILRADAR_API_KEY=your_railradar_key

Get free API keys:
- OpenWeatherMap → https://openweathermap.org/api
- RailRadar API → https://railradar.in/indian-railway-data-api

### 5️⃣ Run Locally
streamlit run app/app.py

Open browser at:
http://localhost:8501

---

## 🌍 Deployment (Streamlit Cloud)

The app is deployed on Streamlit Cloud with automatic GitHub sync.

To deploy your own version:
1. Push project to GitHub
2. Go to share.streamlit.io
3. Connect your repository
4. In Advanced Settings → Secrets, add:

OPENWEATHER_API_KEY = "your_key"
RAILRADAR_API_KEY = "your_key"

5. Deploy 🚀

---

## 📊 Key Insights Discovered

| Insight | Value |
|---------|-------|
| Most Delayed Zone | South Coast Railway (SCoR) — 163 min |
| Best Performing Zone | Western Railway (WR) — 14 min |
| Worst Month | December (winter fog impact) |
| Best Month | August |
| Most Delayed Train | SRC HBJ Humsafar (22170) — 392 min avg |
| Punctuality Order | Superfast > Express > Passenger |

---

## 🎯 Future Enhancements

- Real-time GPS coordinates on India map
- SMS / Email delay alerts
- PNR-based tracking
- Historical journey performance analysis
- Multi-language support (Hindi + regional)
- Voice-based search
- Confidence intervals for predictions
- Push notifications via Telegram bot

---

## 🎓 Educational Value

This project demonstrates:
- Real-world end-to-end ML pipeline
- Data engineering at scale (38M → 7M)
- Feature engineering strategies
- Production deployment
- Multi-API orchestration
- UX-first data application
- Responsible AI (honest data presentation)

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit changes (git commit -m "Add AmazingFeature")
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License.

---

## 👨‍💻 Author

Naman Shukla  
🎓 Final Year Data Science Project  
🔗 GitHub: https://github.com/Namanshukla2  
🌐 Live App: https://train-delay-prediction-projectbynaman.streamlit.app

---

## 🙏 Acknowledgments

- Kaggle for the Indian Railways delay dataset
- RailRadar for real-time train tracking API
- OpenWeatherMap for weather API
- Streamlit for the elegant dashboard framework
- Indian Railways — connecting the nation 🚂

---

⭐ If you found this project useful, please star the repository!