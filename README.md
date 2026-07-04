# 🚂 Train Delay Prediction System

> An industry-level ML system that predicts Indian Railways train delays with real-time tracking, weather integration, and beautiful analytics.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28-red.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Live Demo

🔗 **[Try the Live App](https://your-app-url.streamlit.app)** *(will update after deployment)*

## 📸 Screenshots

*(Add screenshots later)*

## ✨ Features

### 🔮 ML-Powered Delay Prediction
- Predicts train delays in minutes using XGBoost
- Trained on **7.3+ million records** from Indian Railways
- Considers historical patterns, station zones, train types, and seasonal trends
- Smart searchable train and station selection

### 📈 Interactive Analytics Dashboard
- Zone-wise delay analysis across all 18 Indian Railway zones
- Monthly delay trends showing seasonal patterns
- Train type comparisons (Rajdhani, Shatabdi, Superfast, etc.)
- Top 10 most delayed trains with statistics
- Real insights: "SCoR shows 163 min avg delay, December worst month"

### 🗺️ Live Train Tracker
- **Real-time GPS tracking** via RailRadar API
- Beautiful animated journey timeline
- **Weather integration** using OpenWeatherMap API
- ML predictions for upcoming stations
- Handles running, cancelled, completed, and not-started trains
- Progress bar with visual station indicators

### 🎯 Smart User Experience
- Search trains by name, number, or route
- Auto-detection of station zones
- Color-coded delay severity
- Full station names with codes
- Mobile responsive design

## 🧠 Machine Learning Approach

### Dataset
- **Source:** Indian Railways Historical Delay Dataset (Kaggle)
- **Size:** 38.4 million rows → 7.3 million (cleaned & sampled)
- **Coverage:** 7,000+ trains, 8,000+ stations, all 18 zones

### Feature Engineering
- Temporal features (month, day, day of week, season)
- Historical aggregates (train avg delay, station avg delay)
- Route features (total distance, total stops, position in route)
- Zone-wise patterns
- Train type impact
- Combined train+station patterns

### Model
- **Algorithm:** XGBoost Regressor
- **Hyperparameters:** Tuned for delay prediction
- **Performance:**
  - MAE: 20.57 minutes
  - RMSE: 40.05 minutes
  - R²: 0.5431

### Real-Time Layer
- RailRadar API for live train position
- OpenWeatherMap API for weather-based adjustments
- Smart caching for performance (60s live data, 30min weather)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.9+ |
| **ML Framework** | XGBoost, scikit-learn |
| **Data Processing** | Pandas, NumPy |
| **Dashboard** | Streamlit |
| **Charts** | Plotly |
| **Live APIs** | RailRadar, OpenWeatherMap |
| **Deployment** | Streamlit Cloud |
| **Version Control** | Git, GitHub |

## 📁 Project Structure

\`\`\`
train-delay-prediction/
│
├── app/
│   ├── app.py              # Main Streamlit application
│   ├── predictor.py        # ML model loader + prediction logic
│   ├── charts.py           # Plotly chart functions
│   ├── api_client.py       # External API integrations
│   └── map_view.py         # Map visualization (Folium)
│
├── model/
│   ├── xgb_model.pkl       # Trained XGBoost model
│   ├── encoders.pkl        # Label encoders
│   ├── features.pkl        # Feature list
│   ├── lookup_tables.pkl   # Aggregation lookups
│   ├── smart_lookup.pkl    # UI lookup data
│   └── dashboard_data.pkl  # Analytics data
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb    # Data cleaning + feature engineering
│   └── 02_model_training.ipynb   # Model training + evaluation
│
├── data/
│   ├── raw/                # Raw dataset (not in repo)
│   └── processed/          # Processed datasets
│
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
\`\`\`

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
\`\`\`bash
git clone https://github.com/YOUR-USERNAME/train-delay-prediction.git
cd train-delay-prediction
\`\`\`

2. **Create virtual environment**
\`\`\`bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
\`\`\`

3. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Setup API keys**

Create a `.env` file in project root:
\`\`\`env
OPENWEATHER_API_KEY=your_openweathermap_key
RAILRADAR_API_KEY=your_railradar_key
\`\`\`

Get free API keys from:
- [OpenWeatherMap](https://openweathermap.org/api)
- [RailRadar](https://railradar.in/indian-railway-data-api)

5. **Download the dataset** (Optional - for retraining)
\`\`\`bash
kaggle datasets download -d rxydenxd/indian-railways-delay-dataset
\`\`\`

### Running the App

\`\`\`bash
cd app
streamlit run app.py
\`\`\`

Open browser to `http://localhost:8501`

## 🌐 Deployment

Deployed on **Streamlit Cloud** for free hosting.

To deploy your own version:
1. Push code to GitHub
2. Sign in to [Streamlit Cloud](https://share.streamlit.io)
3. Connect repository
4. Add secrets (API keys) in Advanced Settings
5. Deploy!

## 📊 Key Insights Discovered

- **Most Delayed Zone:** South Coast Railway (SCoR) — 163 min avg
- **Best Zone:** Western Railway (WR) — 14 min avg
- **Worst Month:** December (winter fog impact)
- **Best Month:** August
- **Most Delayed Train:** SRC HBJ Humsafar (22170) — 392 min avg
- **Superfast trains** are 40% more punctual than Passenger trains

## 🎯 Future Enhancements

- [ ] Real-time GPS coordinates on map
- [ ] SMS/Email alerts for delays
- [ ] PNR-based tracking
- [ ] Historical journey analysis
- [ ] Multi-language support
- [ ] Voice search
- [ ] Prediction confidence intervals

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Naman Shukla**
- GitHub: [@Namanshukla2](https://github.com/Namanshukla2)
- Project: Final Year Data Science Project

## 🙏 Acknowledgments

- Kaggle for providing the Indian Railways Delay Dataset
- RailRadar for live train tracking API
- OpenWeatherMap for weather API
- Streamlit community for the amazing framework

---

⭐ **Star this repo if you found it useful!**