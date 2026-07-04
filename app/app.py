# ==========================================
# app.py
# Main Streamlit Application
# Train Delay Prediction Dashboard
# User-Friendly UX with searchable dropdowns
# ==========================================

import streamlit as st
import datetime
import os
import joblib
from predictor import predict_delay
from streamlit_folium import st_folium

# ---------- Streamlit Page Config ----------

st.set_page_config(
    page_title="Train Delay Predictor",
    page_icon="🚂",
    layout="wide"
)


# ---------- Load Smart Lookup Data ----------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

smart_lookup = joblib.load(os.path.join(MODEL_DIR, "smart_lookup.pkl"))
station_info = smart_lookup["station_info"]
train_info = smart_lookup["train_info"]
route_lookup = smart_lookup["route_lookup"]


# ---------- Sidebar Navigation ----------

st.sidebar.title("🚂 Train Delay System")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🔮 Delay Predictor", "📈 Analytics",
     "🗺️ Live Tracker", "📋 Data Explorer"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Final Year Data Science Project")
st.sidebar.caption("Built with ❤️ using XGBoost + Streamlit")


# ==========================================
# PAGE 1 — HOME
# ==========================================

if page == "🏠 Home":

    st.title("🚂 Indian Railways — Train Delay Prediction System")
    st.markdown("### An Industry-Level Machine Learning Dashboard")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📊 Rows Trained", "7.3M+")
    with col2:
        st.metric("🚆 Unique Trains", "7,000+")
    with col3:
        st.metric("📍 Stations Covered", "8,000+")

    st.markdown("---")

    st.subheader("📌 About This Project")
    st.write(
        """
        This system predicts **Indian Railways train delays** in advance
        using historical delay data, train metadata, station zones,
        route features and seasonal patterns.

        Built with:
        - 🧠 **XGBoost Regression Model**
        - 📊 **7.3 Million+ Rows** of real data
        - ⚙️ **Feature Engineering** across trains, stations & zones
        - 🌐 **Streamlit Dashboard** for interactive access
        """
    )

    st.info("👉 Use the sidebar to navigate to the Delay Predictor.")


# ==========================================
# PAGE 2 — DELAY PREDICTOR (User-Friendly UX)
# ==========================================

elif page == "🔮 Delay Predictor":

    st.title("🔮 Train Delay Predictor")
    st.write("🔍 Search your train and select the station to check expected delay")

    st.markdown("---")

    # ---------- STEP 1: Select Train ----------

    st.subheader("🚆 Step 1: Select Your Train")

    train_display_list = train_info['display_name'].tolist()

    selected_train = st.selectbox(
        "Search by train name, number, or route",
        options=train_display_list,
        index=0,
        placeholder="Type to search... e.g. 'Rajdhani Delhi', 'Rewanchal', '12301'",
        help="💡 Tip: You can search by train name, number, or route (origin/destination)"
    )

    # Extract train_no and type_code
    selected_train_row = train_info[
        train_info['display_name'] == selected_train
    ].iloc[0]

    train_no = int(selected_train_row['train_no'])
    type_code = selected_train_row['type_code']
    train_name = selected_train_row['train_name']

    # Show train info card
    st.info(
        f"✅ **Selected:** {train_name} | Train #{train_no} | Type: {type_code}"
    )

    st.markdown("---")

    # ---------- STEP 2: Select Station ----------

    st.subheader("📍 Step 2: Select Station on Route")

    if train_no in route_lookup:

        route_stations = route_lookup[train_no]

        # Remove duplicate stations (keep first occurrence)
        seen = set()
        unique_stations = []
        for s in route_stations:
            if s['station_name'] not in seen:
                seen.add(s['station_name'])
                unique_stations.append(s)
        route_stations = unique_stations

        # User-friendly display: "Stop 3 - Unchehra (UHR)"
        route_display = [
            f"Stop {s['station_no']} - {s.get('station_full_name', s['station_name'])} ({s['station_name']})"
            for s in route_stations
        ]

        selected_station = st.selectbox(
            "Choose the station where you want to check delay",
            options=route_display,
            index=0,
            help="💡 Select the station you're waiting at, or the destination station"
        )

        # Extract details
        selected_idx = route_display.index(selected_station)
        station_no = route_stations[selected_idx]['station_no']
        station_name = route_stations[selected_idx]['station_name']
        station_full = route_stations[selected_idx].get(
            'station_full_name', station_name
        )

    else:
        # Fallback: manual station search
        st.warning("⚠️ Route not found for this train. Search station manually.")

        station_display_list = station_info['display_name'].tolist()

        selected_station_manual = st.selectbox(
            "Search station by name or code",
            options=station_display_list,
            index=0,
            placeholder="Type to search... e.g. Delhi, Mumbai"
        )

        selected_station_row = station_info[
            station_info['display_name'] == selected_station_manual
        ].iloc[0]

        station_name = selected_station_row['station_name']
        station_full = selected_station_row['station_full_name']
        station_no = st.number_input(
            "Approximate stop number in route",
            min_value=1, max_value=150, value=5
        )

    # Auto-detect zone
    zone_row = station_info.loc[
        station_info['station_name'] == station_name, 'station_zone'
    ]
    station_zone = zone_row.iloc[0] if not zone_row.empty else "Unknown"

    st.info(
        f"✅ **Station:** {station_full} ({station_name}) | "
        f"Stop #{station_no} | Zone: {station_zone}"
    )

    st.markdown("---")

    # ---------- STEP 3: Select Date ----------

    st.subheader("📅 Step 3: Select Travel Date")

    travel_date = st.date_input(
        "When are you travelling?",
        value=datetime.date.today(),
        help="💡 Check delay for any future or past date"
    )

    st.markdown("---")

    # ---------- Predict Button ----------

    if st.button("🚀 Predict Delay", use_container_width=True, type="primary"):

        month = travel_date.month
        day = travel_date.day
        day_of_week = travel_date.weekday()

        with st.spinner("🔍 Analyzing patterns and predicting delay..."):
            result = predict_delay(
                train_no=train_no,
                station_name=station_name.upper().strip(),
                station_no=station_no,
                station_zone=station_zone,
                type_code=type_code,
                month=month,
                day=day,
                day_of_week=day_of_week
            )

        # ---------- Result Display ----------

        st.markdown("---")
        st.subheader("📊 Prediction Result")

        delay = result["predicted_delay_min"]

        # User-friendly result messages
        if delay < 0:
            st.success(
                f"✅ **Train Likely On Time or Early**\n\n"
                f"Predicted: **{abs(delay):.1f} minutes ahead of schedule**\n\n"
                f"Your train is expected to arrive on time at **{station_full}**."
            )
        elif delay < 10:
            st.success(
                f"✅ **On Time**\n\n"
                f"Predicted Delay: **{delay:.1f} minutes**\n\n"
                f"Expected to arrive on time at **{station_full}**."
            )
        elif delay < 30:
            st.warning(
                f"⚠️ **Minor Delay Expected**\n\n"
                f"Predicted Delay: **{delay:.1f} minutes**\n\n"
                f"Train may reach **{station_full}** with slight delay."
            )
        elif delay < 60:
            st.error(
                f"🚨 **Significant Delay Expected**\n\n"
                f"Predicted Delay: **{delay:.1f} minutes**\n\n"
                f"Plan accordingly for arrival at **{station_full}**."
            )
        else:
            st.error(
                f"🚨🚨 **Major Delay Expected**\n\n"
                f"Predicted Delay: **{delay:.1f} minutes** "
                f"({delay/60:.1f} hours)\n\n"
                f"Consider rescheduling your plans."
            )

        # Prediction breakdown
        st.markdown("### 🔍 Prediction Breakdown")

        c1, c2, c3 = st.columns(3)
        c1.metric("🌦 Season", result["season"])
        c2.metric("🚆 Train Avg Delay", f"{result['train_avg_delay']} min")
        c3.metric("📍 Station Avg Delay", f"{result['station_avg_delay']} min")

        c4, c5 = st.columns(2)
        c4.metric("🛤 Route Distance", f"{result['route_distance_km']} km")
        c5.metric("🚉 Total Stops", result["total_stops"])

        # Explanation expander
        with st.expander("💡 What do these numbers mean?"):
            st.markdown(f"""
            - **🌦 Season:** Current season affects delays (Monsoon = more delays)
            - **🚆 Train Avg Delay:** How late this train usually runs historically ({result['train_avg_delay']} min avg)
            - **📍 Station Avg Delay:** How late trains typically arrive at {station_full} ({result['station_avg_delay']} min avg)
            - **🛤 Route Distance:** Longer routes = more delay accumulation
            - **🚉 Total Stops:** More stops = more potential delays
            """)


# ==========================================
# PAGE 3 — ANALYTICS DASHBOARD
# ==========================================

elif page == "📈 Analytics":

    from charts import (
        plot_zone_delays,
        plot_monthly_trend,
        plot_train_type_delays,
        plot_records_pie,
        format_top_delayed_table
    )

    st.title("📈 Railway Analytics Dashboard")
    st.write("📊 Comprehensive insights from **7.3 Million+** railway records")
    st.markdown("---")

    # ---------- Load Dashboard Data ----------

    @st.cache_data
    def load_dashboard_data():
        return joblib.load(os.path.join(MODEL_DIR, "dashboard_data.pkl"))

    dashboard_data = load_dashboard_data()

    zone_stats = dashboard_data["zone_stats"]
    monthly_stats = dashboard_data["monthly_stats"]
    type_stats = dashboard_data["type_stats"]
    top_delayed = dashboard_data["top_delayed"]
    kpis = dashboard_data["kpis"]

    # ---------- KPI Cards ----------

    st.subheader("📊 Key Performance Indicators")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            label="📈 Total Records",
            value=f"{kpis['total_records']/1_000_000:.1f}M"
        )

    with kpi2:
        st.metric(
            label="🚆 Unique Trains",
            value=f"{kpis['unique_trains']:,}"
        )

    with kpi3:
        st.metric(
            label="📍 Stations",
            value=f"{kpis['unique_stations']:,}"
        )

    with kpi4:
        st.metric(
            label="⏱️ Avg Delay",
            value=f"{kpis['avg_delay_overall']:.1f} min"
        )

    # Alert card for worst zone
    st.error(
        f"🚨 **Most Delayed Zone:** {kpis['worst_zone']} "
        f"with average delay of **{kpis['worst_zone_delay']:.1f} minutes**"
    )

    st.markdown("---")

    # ---------- Zone-Wise Delay Chart ----------

    st.subheader("🌐 Zone-wise Delay Analysis")
    st.write(
        "Compare average delays across all Indian Railway zones. "
        "**Red bars indicate zones with higher delays.**"
    )

    fig_zone = plot_zone_delays(zone_stats)
    st.plotly_chart(fig_zone, use_container_width=True)

    st.markdown("---")

    # ---------- Monthly Trend Chart ----------

    st.subheader("📅 Monthly Delay Patterns")
    st.write(
        "See how delays vary month-by-month across the year. "
        "Useful for identifying seasonal patterns like **monsoon or winter fog**."
    )

    fig_monthly = plot_monthly_trend(monthly_stats)
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.markdown("---")

    # ---------- Train Type Analysis ----------

    st.subheader("🚄 Train Type Comparison")

    c1, c2 = st.columns(2)

    with c1:
        st.write("**Average delay by train category**")
        fig_type = plot_train_type_delays(type_stats)
        st.plotly_chart(fig_type, use_container_width=True)

    with c2:
        st.write("**Data distribution across types**")
        fig_pie = plot_records_pie(type_stats)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # ---------- Top Delayed Trains ----------

    st.subheader("🚨 Top 10 Most Delayed Trains")
    st.write(
        "Trains with the highest average delay historically "
        "(filtered for statistical significance — minimum 100 records)."
    )

    top_delayed_display = format_top_delayed_table(top_delayed)
    st.dataframe(
        top_delayed_display,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

       # ---------- Insights Section ----------

    st.subheader("💡 Key Insights")

    col_a, col_b = st.columns(2)

    with col_a:
        # Worst zone with full name
        worst_zone_full = kpis.get('worst_zone_full', kpis['worst_zone'])

        st.info(
            f"**🌐 Zone Analysis**\n\n"
            f"Out of all Indian Railway zones analyzed, "
            f"**{worst_zone_full} ({kpis['worst_zone']})** shows the highest "
            f"average delay of **{kpis['worst_zone_delay']:.1f} minutes**."
        )

        # Best performing zone (least delay)
        best_zone_row = zone_stats.iloc[-1]
        best_zone_name = best_zone_row.get(
            'zone_full_name', best_zone_row['station_zone']
        )

        st.success(
            f"**✅ Best Performing Zone**\n\n"
            f"**{best_zone_name} ({best_zone_row['station_zone']})** performs "
            f"best with only **{best_zone_row['avg_delay']:.1f} minutes** "
            f"average delay."
        )

    with col_b:
        # Best and worst months
        best_month = monthly_stats.loc[monthly_stats['avg_delay'].idxmin()]
        worst_month = monthly_stats.loc[monthly_stats['avg_delay'].idxmax()]

        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        st.warning(
            f"**📅 Most Delayed Month**\n\n"
            f"**{month_names[int(worst_month['month'])]}** shows the highest "
            f"average delay of **{worst_month['avg_delay']:.1f} minutes**."
        )

        st.success(
            f"**✅ Best Month to Travel**\n\n"
            f"**{month_names[int(best_month['month'])]}** shows the lowest "
            f"average delay of **{best_month['avg_delay']:.1f} minutes**."
        )

    st.markdown("---")

    st.caption(
        "📌 Data analyzed from Indian Railways historical delay records. "
        "Analysis powered by XGBoost ML model."
    )

# ==========================================
# PAGE 4 — LIVE TRAIN TRACKER
# ==========================================

elif page == "🗺️ Live Tracker":

    from api_client import (
        get_live_train_status,
        parse_live_train_data,
        get_weather_by_city,
        calculate_weather_adjustment
    )
    import streamlit.components.v1 as components

    st.title("🚂 Live Train Tracker")
    st.write(
        "🔴 **Real-time tracking** with ML-powered delay predictions "
        "and weather insights."
    )
    st.markdown("---")

    # ---------- Smart Train Search ----------

    st.subheader("🚆 Search Your Train")

    reliable_types = [
        'RAJ-TRAINS', 'SHT-TRAINS', 'DURONTO', 'GARIB-RATH',
        'SF-TRAINS', 'EXP-TRAINS', 'MAIL-TRAINS',
        'HUMSAFAR', 'TEJAS', 'VANDE-BHARAT'
    ]

    filtered_trains = train_info[
        train_info['type_code'].isin(reliable_types)
    ]

    train_display_list = filtered_trains['display_name'].tolist()

    selected_train_display = st.selectbox(
        "Search by train name, number, or route",
        options=train_display_list,
        index=0,
        placeholder="Type... e.g. 'Rajdhani Delhi', 'Shatabdi', '12951'",
        help="💡 Showing trains with reliable live tracking",
        key="tracker_train_search"
    )

    selected_train_row = filtered_trains[
        filtered_trains['display_name'] == selected_train_display
    ].iloc[0]

    raw_train_no = int(selected_train_row['train_no'])
    selected_train_no = str(raw_train_no).zfill(5)

    col_info, col_button = st.columns([3, 1])

    with col_info:
        st.info(
            f"✅ **Selected:** {selected_train_row['train_name']} "
            f"(Train #{selected_train_no})"
        )

    with col_button:
        track_button = st.button(
            "🔴 Track Live",
            use_container_width=True,
            type="primary"
        )

    st.markdown("---")

    # ---------- Fetch & Display Live Data ----------

    if track_button:

        with st.spinner("🛰️ Fetching live train data..."):
            api_response = get_live_train_status(selected_train_no)

        # ---------- Error Handling ----------

        if not api_response.get("success"):
            error_msg = api_response.get('error', 'Unknown error')

            if "400" in error_msg:
                st.warning(
                    f"⚠️ **Train {selected_train_no} not available for live tracking**\n\n"
                    "This train might be a special/seasonal train not covered.\n\n"
                    "💡 **Try popular trains:**\n"
                    "- **12951** - Mumbai Rajdhani\n"
                    "- **12001** - Bhopal Shatabdi\n"
                    "- **12919** - Malwa Express\n"
                    "- **12301** - Howrah Rajdhani"
                )
                st.stop()

            elif "not found" in error_msg.lower() or "not running" in error_msg.lower():
                st.warning(
                    f"⚠️ **Train {selected_train_no} is not running today**\n\n"
                    "💡 Try popular Rajdhani/Shatabdi trains."
                )
                st.stop()

            elif "rate limit" in error_msg.lower():
                st.error("🚫 **API Rate Limit Reached** - Wait 1 minute.")
                st.stop()

            elif "invalid api key" in error_msg.lower():
                st.error("🔑 **API Key Issue**")
                st.stop()

            else:
                st.error(f"❌ **Error:** {error_msg}")
                st.stop()

        # Parse data
        train_data = parse_live_train_data(api_response)

        if not train_data:
            st.error("❌ Failed to parse live data")
            st.stop()

        # ---------- Detect Train Status ----------

        route = train_data.get("route", [])
        current_seq = train_data.get("current_sequence", 1)
        current_speed = train_data.get("current_speed", 0)
        current_delay = train_data.get("current_delay", 0)

        api_status = train_data.get("status", "unknown").lower()
        is_live = train_data.get("is_live", False)

        train_running = api_status == "running"
        train_completed = api_status == "completed"
        train_not_started = api_status == "not-started"
        train_cancelled = api_status == "cancelled"

        # Fallback status detection
        if api_status == "unknown" and route:
            first_actual_dep = route[0].get("actualDeparture")
            last_actual_arr = route[-1].get("actualArrival")

            if not first_actual_dep:
                train_not_started = True
            elif last_actual_arr and not is_live:
                train_completed = True
            else:
                train_running = True

        # ---------- Header ----------

        st.markdown(
            f"### 🚂 {train_data['train_name']} ({train_data['train_number']})"
        )

        route_col1, route_col2 = st.columns(2)
        with route_col1:
            st.markdown(
                f"**From:** {train_data['source_station']} "
                f"({train_data['source_code']})"
            )
        with route_col2:
            st.markdown(
                f"**To:** {train_data['destination_station']} "
                f"({train_data['destination_code']})"
            )

        # ---------- Status Banner (Single, No Duplicate) ----------

        if train_cancelled:
            st.error(
                f"🚫 **TRAIN CANCELLED**\n\n"
                f"This train has been cancelled for today."
            )
            st.stop()

        if train_running or is_live:
            last_update = train_data.get('last_updated', '')
            update_time = last_update.split("T")[1][:8] if "T" in last_update else "N/A"
            update_date = last_update.split("T")[0] if "T" in last_update else ""

            st.success(
                f"🔴 **LIVE TRACKING** • "
                f"Last updated: {update_time} IST on {update_date}"
            )

        elif train_not_started:
            if route and route[0].get("scheduledDeparture"):
                sched_dep = route[0]["scheduledDeparture"]
                dep_time = sched_dep.split("T")[1][:5] if "T" in sched_dep else "N/A"
                dep_date = sched_dep.split("T")[0] if "T" in sched_dep else ""

                st.warning(
                    f"⏳ **TRAIN NOT STARTED YET**\n\n"
                    f"🕐 Scheduled Departure: **{dep_time}** on {dep_date}\n\n"
                    f"📍 From: {train_data['source_station']}\n\n"
                    "Live tracking will begin once journey starts."
                )

                st.markdown("---")
                st.markdown("### 📋 Train Info")

                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    st.metric("🎯 Distance", f"{train_data.get('total_distance', 0)} km")
                with info_col2:
                    st.metric("🚉 Stops", train_data.get('total_halts', 0))
                with info_col3:
                    st.metric("🚄 Max Speed", f"{train_data.get('max_speed', 0)} km/h")

                st.stop()
            else:
                st.warning("⏳ Train hasn't started yet")
                st.stop()

        elif train_completed and not is_live:
            st.info(
                f"✅ **Previous Journey Completed**\n\n"
                f"Train has completed its last journey to "
                f"{train_data['destination_station']}.\n\n"
                f"💡 Next journey may not have started yet."
            )

            st.markdown("---")
            st.markdown("### 📋 Last Journey Details")

            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.metric("🎯 Distance", f"{train_data.get('total_distance', 0)} km")
            with info_col2:
                st.metric("🚉 Total Stops", train_data.get('total_halts', 0))

            st.stop()

        else:
            st.warning(
                f"⚠️ **Status Unclear** - Showing available data."
            )

        # ---------- Exceptions ----------

        if train_data.get("has_exceptions"):
            for exception in train_data["exceptions"]:
                st.error(
                    f"⚠️ **{exception.get('type', 'Alert')}:** "
                    f"{exception.get('message', '')}"
                )

        # ---------- Live Status Cards (With Station Names) ----------

               # ---------- Live Status Cards (Honest Data Presentation) ----------

        st.markdown("### 📊 Current Status")

        # Get current station full name
        current_station_name = ""
        current_station_code = train_data.get("current_station_code", "N/A")
        current_station_status = "departed"  # departed or arrived
        for s in route:
            if s.get("sequence") == current_seq:
                current_station_name = s.get("stationName", "")
                current_station_status = s.get("status", "unknown")
                break

        # Get next halt full name
        next_halt_code = train_data.get("next_halt_code", "N/A")
        next_halt_name = train_data.get("next_halt_name", "")

        # Calculate time since last update
        from datetime import datetime, timezone, timedelta
        last_update = train_data.get('last_updated', '')
        time_since_update = "Unknown"
        minutes_ago = 0
        
        if last_update and "T" in last_update:
            try:
                # Parse ISO format with timezone
                update_dt = datetime.fromisoformat(last_update)
                now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                diff = now_ist - update_dt
                minutes_ago = int(diff.total_seconds() / 60)
                
                if minutes_ago < 1:
                    time_since_update = "Just now"
                elif minutes_ago < 60:
                    time_since_update = f"{minutes_ago} min ago"
                else:
                    hours = minutes_ago // 60
                    time_since_update = f"{hours}h {minutes_ago % 60}m ago"
            except:
                time_since_update = "Recently"

        # Determine location context (departed = moving toward next, arrived = at station)
        if current_station_status == "departed":
            location_label = "🚉 Last Departed From"
            location_help = f"Train departed from this station, now en route to {next_halt_name or 'next halt'}"
        elif current_station_status == "arrived":
            location_label = "📍 Currently At"
            location_help = "Train is currently at this station"
        else:
            location_label = "📍 Last Known Location"
            location_help = "Last confirmed station"

        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

        with stat_col1:
            st.metric(
                location_label,
                current_station_name if current_station_name else current_station_code,
                help=location_help
            )
            if current_station_name:
                st.caption(f"Code: `{current_station_code}`")

        with stat_col2:
            delay_delta = None
            if current_delay > 0:
                if current_delay < 15:
                    delay_delta = "Minor"
                elif current_delay < 60:
                    delay_delta = "Moderate"
                else:
                    delay_delta = "Major"
            else:
                delay_delta = "On time"

            st.metric(
                "⏱️ Delay",
                f"{current_delay} min",
                delta=delay_delta,
                delta_color="inverse" if current_delay > 30 else "normal"
            )

        with stat_col3:
            # Replace speed with more useful info - last update time
            update_color = "normal" if minutes_ago < 15 else "inverse"
            st.metric(
                "🕐 Last Update",
                time_since_update,
                delta="Live" if minutes_ago < 5 else f"{minutes_ago}m stale",
                delta_color=update_color,
                help="Data may be delayed 5-15 min from actual position"
            )

        with stat_col4:
            st.metric(
                "🎯 Next Stop",
                next_halt_name if next_halt_name else next_halt_code,
                delta=f"{train_data.get('next_halt_distance', 0)} km away"
            )
            if next_halt_name:
                st.caption(f"Code: `{next_halt_code}`")

        # ---------- Data Source Disclaimer ----------
        
        st.info(
            "ℹ️ **About This Data:** Location is based on last confirmed station report. "
            "Actual train position may be **5-15 km ahead** of shown location. "
            "Real-time GPS tracking requires premium API access."
        )

        st.markdown("---")

        # ---------- Journey Progress Bar ----------

        st.markdown("### 🛤️ Journey Progress")

        total_stations = len(route)
        progress_pct = (current_seq / total_stations) if total_stations > 0 else 0

        st.progress(progress_pct)
        st.caption(
            f"🚂 **{int(progress_pct * 100)}%** completed "
            f"({current_seq} of {total_stations} stations) • "
            f"Currently at: **{current_station_name}** (`{current_station_code}`)"
        )

               # ---------- Build HALT-ONLY Timeline HTML ----------

        # Filter only halt stations
        halt_stations = [
            s for s in route
            if s.get("isHalt", False) is True
        ]

        stations_html = ""

        for idx, station in enumerate(halt_stations):
            seq = station.get("sequence", idx + 1)
            code = station.get("stationCode", "")
            full_name = station.get("stationName", "")

            # Truncate long names
            display_name = full_name if len(full_name) <= 16 else full_name[:14] + ".."

            # Get delay
            delay = (
                station.get("delayArrival")
                or station.get("delayDeparture")
                or 0
            )

            # ---------- COLOR LOGIC ----------
            if delay <= 9:
                dot_color = "#27AE60"   # Green
                delay_text = "On Time"
            elif delay <= 24:
                dot_color = "#F1C40F"   # Yellow
                delay_text = f"+{delay}m"
            else:
                dot_color = "#E74C3C"   # Red
                delay_text = f"+{delay}m"

            # Override for current station
            if seq == current_seq:
                dot_color = "#2980B9"
                delay_text = f"Now • {current_delay}m"

            stations_html += f"""
                <div style="
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    min-width:130px;
                    margin:0 12px;
                    text-align:center;
                ">
                    <div style="
                        width:36px;
                        height:36px;
                        border-radius:50%;
                        background:{dot_color};
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        color:white;
                        font-weight:bold;
                        font-size:14px;
                        margin-bottom:8px;
                    ">
                        {idx+1}
                    </div>

                    <div style="
                        font-size:13px;
                        font-weight:600;
                        line-height:1.2;
                    ">
                        {display_name}
                    </div>

                    <div style="
                        font-size:11px;
                        color:#95A5A6;
                        margin-top:2px;
                    ">
                        ({code})
                    </div>

                    <div style="
                        font-size:11px;
                        margin-top:4px;
                        font-weight:bold;
                        color:{dot_color};
                    ">
                        {delay_text}
                    </div>
                </div>
            """

        complete_html = f"""
        <div style="
            display:flex;
            overflow-x:auto;
            padding:20px;
            background:linear-gradient(90deg,#1e1e2e,#2d2d44);
            border-radius:12px;
        ">
            {stations_html}
        </div>
        """

        components.html(complete_html, height=200, scrolling=True)

        st.markdown("---")
        
        # ---------- Detailed Station List (Optimized) ----------

        st.markdown("### 📋 Station-wise Details")

        # Configuration
        PASSED_TO_SHOW = 5
        UPCOMING_TO_SHOW = 10
        WEATHER_EVERY_N = 3

        # Filter to nearby stations
        nearby_route = []
        start_idx = max(0, current_seq - PASSED_TO_SHOW - 1)
        end_idx = min(len(route), current_seq + UPCOMING_TO_SHOW)

        important_indices = {0, len(route) - 1, current_seq - 1}

        for idx, station in enumerate(route):
            if start_idx <= idx <= end_idx or idx in important_indices:
                nearby_route.append(station)

        showing_count = len(nearby_route)

        if total_stations > showing_count:
            st.info(
                f"💡 Showing **{showing_count} nearby stations** out of {total_stations} "
                f"total for faster loading. All stations visible in Journey Progress above."
            )

        # Fetch Weather (only for key upcoming stations)
        upcoming_predictions = {}
        upcoming_stations_for_weather = []

        for idx, station in enumerate(nearby_route):
            seq = station.get("sequence", 0)
            if seq > current_seq:
                should_fetch = (
                    idx % WEATHER_EVERY_N == 0 or
                    seq == current_seq + 1 or
                    seq == route[-1].get("sequence")
                )
                if should_fetch:
                    upcoming_stations_for_weather.append(station)

        with st.spinner(
            f"🧠 Generating predictions for {len(upcoming_stations_for_weather)} key stations..."
        ):
            for station in upcoming_stations_for_weather:
                station_name = station.get("stationName", "")
                station_code = station.get("stationCode", "")

                weather = get_weather_by_city(station_name)
                base_delay = current_delay
                adjustment = calculate_weather_adjustment(weather, base_delay)

                upcoming_predictions[station_code] = {
                    "predicted_delay": adjustment["adjusted_delay"],
                    "weather": weather
                }

        # Display Stations
        for station in nearby_route:
            seq = station.get("sequence", 0)
            name = station.get("stationName", "")
            code = station.get("stationCode", "")

            # PASSED STATIONS
            if seq < current_seq:
                delay = station.get("delayArrival") or station.get("delayDeparture") or 0
                actual_arr = station.get("actualArrival", "")
                arr_time = actual_arr.split("T")[1][:5] if "T" in actual_arr else "—"

                c1, c2, c3 = st.columns([1, 3, 2])
                with c1:
                    st.markdown("### ✅")
                with c2:
                    st.markdown(f"**{seq}. {name}** (`{code}`)")
                    st.caption(f"Arrived at {arr_time}")
                with c3:
                    if delay > 0:
                        st.warning(f"+{delay} min late")
                    else:
                        st.success("On time")

                       # CURRENT STATION (Honest Display)
            elif seq == current_seq:
                # Determine status text
                if current_station_status == "departed":
                    status_line = f"🚂 Departed • En route to {next_halt_name}"
                    header_emoji = "🚉"
                    header_text = "LAST DEPARTED FROM"
                elif current_station_status == "arrived":
                    status_line = "📍 Currently at this station"
                    header_emoji = "📍"
                    header_text = "CURRENTLY AT"
                else:
                    status_line = "📡 Last known location"
                    header_emoji = "📍"
                    header_text = "LAST KNOWN LOCATION"

                current_card_html = f"""
                <div style="
                    background: linear-gradient(135deg, #E74C3C, #C0392B);
                    padding: 24px;
                    border-radius: 14px;
                    color: white;
                    margin: 15px 0;
                    box-shadow: 0 6px 25px rgba(231, 76, 60, 0.4);
                    font-family: Arial, sans-serif;
                ">
                    <div style="font-size: 12px; opacity: 0.9; letter-spacing: 1px; margin-bottom: 8px;">
                        {header_emoji} {header_text}
                    </div>
                    <h2 style="margin: 0 0 12px 0; color: white; font-size: 26px;">
                        {name}
                    </h2>
                    <p style="margin: 8px 0; font-size: 14px; opacity: 0.95;">
                        Code: <b>{code}</b> &nbsp;•&nbsp; Stop #{seq}
                    </p>
                    <div style="
                        background: rgba(255,255,255,0.15);
                        padding: 10px 14px;
                        border-radius: 8px;
                        margin-top: 12px;
                    ">
                        <p style="margin: 0; font-size: 14px;">
                            {status_line}
                        </p>
                        <p style="margin: 6px 0 0 0; font-size: 15px;">
                            ⏱️ <b>{current_delay} min delay</b> &nbsp;•&nbsp; 
                            🕐 Updated {time_since_update}
                        </p>
                    </div>
                </div>
                """
                components.html(current_card_html, height=210)

            # UPCOMING STATIONS
            else:
                pred = upcoming_predictions.get(code, {})
                pred_delay = pred.get("predicted_delay", current_delay)
                weather = pred.get("weather", {})

                c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
                with c1:
                    st.markdown("### 🔮")
                with c2:
                    st.markdown(f"**{seq}. {name}** (`{code}`)")
                    sched_arr = station.get("scheduledArrival", "")
                    sched_time = sched_arr.split("T")[1][:5] if "T" in sched_arr else "—"
                    st.caption(f"Scheduled: {sched_time}")
                with c3:
                    if weather and weather.get("success"):
                        st.markdown(
                            f"{weather['icon']} {weather['temperature']}°C  \n"
                            f"_{weather['condition']}_"
                        )
                    else:
                        st.markdown("_—_")
                with c4:
                    if pred_delay < 10:
                        st.success(f"✅ +{pred_delay:.0f}m")
                    elif pred_delay < 30:
                        st.warning(f"⚠️ +{pred_delay:.0f}m")
                    else:
                        st.error(f"🚨 +{pred_delay:.0f}m")

        st.markdown("---")

        # ---------- Journey Summary ----------

        st.markdown("### 📊 Journey Summary")

        sum_col1, sum_col2, sum_col3 = st.columns(3)
        with sum_col1:
            st.metric("🎯 Total Distance", f"{train_data.get('total_distance', 0)} km")
        with sum_col2:
            st.metric("📈 Progress", f"{int(progress_pct * 100)}%")
        with sum_col3:
            st.metric("🚉 Total Stops", train_data.get("total_halts", 0))

        weather_alerts = [
            p for p in upcoming_predictions.values()
            if p.get("weather") and p["weather"].get("delay_risk") in ["high", "medium"]
        ]

        if weather_alerts:
            st.warning(
                f"🌦 **Weather Alert:** {len(weather_alerts)} upcoming stations "
                f"may experience weather-related delays."
            )
        else:
            st.success("✅ Clear weather conditions on remaining route!")

        st.info("💡 **Tip:** Click 'Track Live' again to refresh data.")

# ==========================================
# PAGE 5 — DATA EXPLORER (Placeholder)
# ==========================================

elif page == "📋 Data Explorer":
    st.title("📋 Data Explorer")
    st.info("🚧 Coming Soon — Raw data browser with filters.")