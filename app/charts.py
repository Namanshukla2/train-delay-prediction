# ==========================================
# charts.py
# Contains all Plotly chart functions
# for the Analytics Dashboard page
# ==========================================

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ---------- Chart 1: Zone-Wise Delay ----------

# ---------- Chart 1: Zone-Wise Delay (with Full Names) ----------

def plot_zone_delays(zone_stats: pd.DataFrame):
    """
    Bar chart showing average delay by railway zone with full names.
    """
    df_plot = zone_stats.head(15).copy()
    
    # Use full name if available, else zone code
    if 'zone_full_name' in df_plot.columns:
        df_plot['display_zone'] = df_plot['zone_full_name']
    else:
        df_plot['display_zone'] = df_plot['station_zone']
    
    fig = px.bar(
        df_plot,
        x='display_zone',
        y='avg_delay',
        color='avg_delay',
        color_continuous_scale='Reds',
        title='🌐 Average Delay by Railway Zone',
        labels={
            'display_zone': 'Railway Zone',
            'avg_delay': 'Average Delay (minutes)'
        },
        text='avg_delay',
        hover_data={'station_zone': True}
    )

    fig.update_traces(
        texttemplate='%{text:.1f} min',
        textposition='outside'
    )

    fig.update_layout(
        showlegend=False,
        height=550,
        xaxis_tickangle=-45
    )

    return fig

    
# ---------- Chart 2: Monthly Trend ----------

def plot_monthly_trend(monthly_stats: pd.DataFrame):
    """
    Line chart showing average delay by month.
    Shows seasonal patterns.
    """
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    df_plot = monthly_stats.copy()
    df_plot['month_name'] = df_plot['month'].map(month_names)

    fig = px.line(
        df_plot,
        x='month_name',
        y='avg_delay',
        markers=True,
        title='📅 Monthly Delay Trend',
        labels={
            'month_name': 'Month',
            'avg_delay': 'Average Delay (minutes)'
        },
        line_shape='spline'
    )

    fig.update_traces(
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=10, color='#FF6B6B')
    )

    fig.update_layout(
        height=450,
        hovermode='x unified'
    )

    return fig


# ---------- Chart 3: Train Type Distribution ----------

def plot_train_type_delays(type_stats: pd.DataFrame):
    """
    Pie chart / Bar chart showing delay by train type.
    """
    fig = px.bar(
        type_stats,
        x='type_code',
        y='avg_delay',
        color='avg_delay',
        color_continuous_scale='Viridis',
        title='🚄 Average Delay by Train Type',
        labels={
            'type_code': 'Train Type',
            'avg_delay': 'Average Delay (minutes)'
        },
        text='avg_delay'
    )

    fig.update_traces(
        texttemplate='%{text:.1f} min',
        textposition='outside'
    )

    fig.update_layout(
        showlegend=False,
        height=500,
        xaxis_tickangle=-30
    )

    return fig


# ---------- Chart 4: Records Distribution Pie ----------

def plot_records_pie(type_stats: pd.DataFrame):
    """
    Pie chart showing distribution of records across train types.
    """
    fig = px.pie(
        type_stats,
        values='total_records',
        names='type_code',
        title='📊 Data Distribution by Train Type',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )

    fig.update_layout(height=450)

    return fig


# ---------- Chart 5: Top Delayed Trains Table ----------

def format_top_delayed_table(top_delayed: pd.DataFrame):
    """
    Format the top delayed trains for display.
    """
    df_display = top_delayed.copy()
    df_display['avg_delay'] = df_display['avg_delay'].round(2)
    df_display = df_display.rename(columns={
        'train_no': 'Train No',
        'train_name': 'Train Name',
        'type_code': 'Type',
        'avg_delay': 'Avg Delay (min)',
        'total_records': 'Total Records'
    })

    columns_order = [
        'Train No', 'Train Name', 'Type',
        'Avg Delay (min)', 'Total Records'
    ]
    df_display = df_display[columns_order]

    return df_display