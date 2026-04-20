import streamlit as st
import pandas as pd
import sqlite3
import os
import time
import altair as alt

st.set_page_config(page_title="HMI SCADA | Molding Press Systems", layout="wide", initial_sidebar_state="expanded")

# Industrial Grade HMI/SCADA Theme CSS
st.markdown("""
<style>
    /* Global background and text */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-bottom: 2px solid #333333;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    
    /* Metrics / KPIs - Digital Display Style */
    div[data-testid="metric-container"] {
        background-color: #000000;
        border: 2px solid #333333;
        border-radius: 2px;
        padding: 10px 15px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    div[data-testid="metric-container"] label {
        color: #888888;
        font-family: 'Segoe UI', Roboto, sans-serif;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 1px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #00FF00; /* Digital green */
        font-family: 'Consolas', 'Courier New', monospace;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        border-right: 1px solid #333333;
    }
    
    /* Industrial System Buttons */
    .stButton > button {
        width: 100%;
        background-color: #2D2D30;
        color: #E0E0E0;
        border: 1px solid #404040;
        border-radius: 2px;
        padding: 8px;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        transition: all 0.2s;
        margin-bottom: 5px;
    }
    .stButton > button:hover {
        background-color: #3E3E42;
        border-color: #007ACC;
        color: #FFFFFF;
    }
    .stButton > button:active, .stButton > button:focus {
        background-color: #007ACC;
        color: #FFFFFF;
        border-color: #007ACC;
    }
    
    /* Alerts and status text */
    .status-normal { 
        color: #00C853; 
        font-family: 'Consolas', monospace; 
        font-weight: bold; 
        background: #000; 
        padding: 5px 10px; 
        border: 1px solid #00C853; 
        border-radius: 2px; 
        display: inline-block; 
    }
    .status-critical { 
        color: #D50000; 
        font-family: 'Consolas', monospace; 
        font-weight: bold; 
        background: #000; 
        padding: 5px 10px; 
        border: 1px solid #D50000; 
        border-radius: 2px; 
        display: inline-block; 
        animation: blink 1s infinite; 
    }
    .status-warning { 
        color: #FFD600; 
        font-family: 'Consolas', monospace; 
        font-weight: bold; 
        background: #000; 
        padding: 5px 10px; 
        border: 1px solid #FFD600; 
        border-radius: 2px; 
        display: inline-block; 
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    /* Dataframes / Tables */
    .stDataFrame {
        font-family: 'Consolas', 'Courier New', monospace;
    }
    
    /* Hide the top padding */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'molding.db')
    return sqlite3.connect(db_path, check_same_thread=False, timeout=15)

# Industrial color schemes for each machine (High contrast against black)
SYSTEM_COLORS = {
    1: {"primary": "#FF3333", "secondary": "#FF6666"},  # Red
    2: {"primary": "#33FF33", "secondary": "#66FF66"},  # Green
    3: {"primary": "#33CCFF", "secondary": "#66D9FF"},  # Cyan
    4: {"primary": "#FF9933", "secondary": "#FFB366"},  # Orange
    5: {"primary": "#CC33FF", "secondary": "#D966FF"},  # Magenta
    6: {"primary": "#FFFF33", "secondary": "#FFFF66"}   # Yellow
}

# Data caching with exactly 5-second TTL
def get_machine_data_nocache(machine_id=None, limit=100):
    conn = get_connection()
    try:
        if machine_id:
            query = '''
                SELECT sr.*, m.machine_name 
                FROM sensor_readings sr
                JOIN machines m ON sr.machine_id = m.machine_id
                WHERE sr.machine_id = ?
                ORDER BY sr.timestamp DESC LIMIT ?
            '''
            df = pd.read_sql(query, conn, params=(machine_id, limit))
        else:
            query = '''
                SELECT sr.*, m.machine_name 
                FROM sensor_readings sr
                JOIN machines m ON sr.machine_id = m.machine_id
                ORDER BY sr.timestamp DESC LIMIT ?
            '''
            df = pd.read_sql(query, conn, params=(limit,))
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        # Sort ascending for time series charts
        df = df.sort_values(by='timestamp')
        return df
    finally:
        conn.close()

def get_latest_readings_nocache():
    conn = get_connection()
    try:
        query = '''
            SELECT sr.*, m.machine_name 
            FROM sensor_readings sr
            JOIN machines m ON sr.machine_id = m.machine_id
            WHERE sr.timestamp = (
                SELECT MAX(timestamp) 
                FROM sensor_readings sr2 
                WHERE sr2.machine_id = sr.machine_id
            )
        '''
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_alerts_nocache(machine_id=None):
    conn = get_connection()
    try:
        if machine_id:
            query = '''
                SELECT a.timestamp, m.machine_name, a.type, a.severity 
                FROM alerts a
                JOIN machines m ON a.machine_id = m.machine_id
                WHERE a.machine_id = ? AND a.resolved = 0
                ORDER BY a.timestamp DESC LIMIT 10
            '''
            return pd.read_sql(query, conn, params=(machine_id,))
        else:
            query = '''
                SELECT a.timestamp, m.machine_name, a.type, a.severity 
                FROM alerts a
                JOIN machines m ON a.machine_id = m.machine_id
                WHERE a.resolved = 0
                ORDER BY a.timestamp DESC LIMIT 10
            '''
            return pd.read_sql(query, conn)
    finally:
        conn.close()

@st.cache_data(ttl=15)
def get_machines_cached():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM machines ORDER BY machine_id", conn)
    finally:
        conn.close()

def get_system_status(df, machine_id):
    machine_df = df[df['machine_id'] == machine_id]
    if machine_df.empty:
        return "OFFLINE", "⚫"
    
    latest = machine_df.iloc[0]
    
    if latest['hydraulic_pressure'] > 190:
        return "CRITICAL", "🔴"
    elif latest['hydraulic_pressure'] > 180 or latest['platen_temp_upper'] > 190:
        return "WARNING", "🟡"
    else:
        return "NORMAL", "🟢"

def create_optimized_charts(df, machine_id, color_scheme):
    if df.empty:
        return None, None
    
    machine_df = df[df['machine_id'] == machine_id].copy()
    if machine_df.empty:
        return None, None
    
    if len(machine_df) > 50:
        machine_df = machine_df.iloc[::max(1, len(machine_df) // 50)]
    
    # Industrial chart styling
    chart_bg = '#121212'
    grid_color = '#2A2A2A'
    text_color = '#AAAAAA'
    
    # Temperature Area Chart
    base_t = alt.Chart(machine_df).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(title='', gridColor=grid_color, labelColor=text_color, tickColor=text_color, domainColor=text_color)),
        y=alt.Y('platen_temp_upper:Q', scale=alt.Scale(zero=False, padding=10), 
                axis=alt.Axis(title='TEMP (°C)', gridColor=grid_color, labelColor=text_color, titleColor=text_color, tickColor=text_color, domainColor=text_color)),
        tooltip=['timestamp:T', 'platen_temp_upper:Q', 'cycle_state:N']
    )
    
    line_t = base_t.mark_line(strokeWidth=2, color=color_scheme["primary"])
    area_t = base_t.mark_area(
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color=color_scheme["primary"], offset=0),
                alt.GradientStop(color=chart_bg, offset=1)
            ],
            x1=1, x2=1, y1=1, y2=0
        ),
        opacity=0.3
    )
    
    temp_chart = (area_t + line_t).properties(
        height=300,
        title=alt.TitleParams(f'SYS_{machine_id} - PLATEN TEMPERATURE', color='#FFFFFF', font='Segoe UI', fontSize=12, anchor='start')
    ).configure(background=chart_bg).configure_view(strokeWidth=1, stroke='#333333')
    
    # Pressure Area Chart
    base_p = alt.Chart(machine_df).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(title='', gridColor=grid_color, labelColor=text_color, tickColor=text_color, domainColor=text_color)),
        y=alt.Y('hydraulic_pressure:Q', scale=alt.Scale(zero=False, padding=10), 
                axis=alt.Axis(title='PRESSURE (BAR)', gridColor=grid_color, labelColor=text_color, titleColor=text_color, tickColor=text_color, domainColor=text_color)),
        tooltip=['timestamp:T', 'hydraulic_pressure:Q', 'cycle_state:N']
    )
    
    line_p = base_p.mark_line(strokeWidth=2, color=color_scheme["secondary"])
    area_p = base_p.mark_area(
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color=color_scheme["secondary"], offset=0),
                alt.GradientStop(color=chart_bg, offset=1)
            ],
            x1=1, x2=1, y1=1, y2=0
        ),
        opacity=0.3
    )
    
    pressure_chart = (area_p + line_p).properties(
        height=300,
        title=alt.TitleParams(f'SYS_{machine_id} - HYDRAULIC PRESSURE', color='#FFFFFF', font='Segoe UI', fontSize=12, anchor='start')
    ).configure(background=chart_bg).configure_view(strokeWidth=1, stroke='#333333')
    
    return temp_chart, pressure_chart

def create_optimized_overview_charts(df):
    if df.empty:
        return None, None
    
    if len(df) > 200:
        df = df.iloc[::max(1, len(df) // 200)]
        
    chart_bg = '#121212'
    grid_color = '#2A2A2A'
    text_color = '#AAAAAA'
    
    temp_chart = alt.Chart(df).mark_line(strokeWidth=1.5).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(title='', gridColor=grid_color, labelColor=text_color, tickColor=text_color, domainColor=text_color)),
        y=alt.Y('platen_temp_upper:Q', scale=alt.Scale(zero=False, padding=10), 
                axis=alt.Axis(title='TEMP (°C)', gridColor=grid_color, labelColor=text_color, titleColor=text_color, tickColor=text_color, domainColor=text_color)),
        color=alt.Color('machine_name:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title="SYSTEM", labelColor=text_color, titleColor=text_color)),
        tooltip=['timestamp:T', 'machine_name:N', 'platen_temp_upper:Q', 'cycle_state:N']
    ).properties(
        height=320,
        title=alt.TitleParams('GLOBAL THERMAL OVERVIEW', color='#FFFFFF', font='Segoe UI', fontSize=12, anchor='start')
    ).configure(background=chart_bg).configure_view(strokeWidth=1, stroke='#333333')
    
    pressure_chart = alt.Chart(df).mark_line(strokeWidth=1.5).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(title='', gridColor=grid_color, labelColor=text_color, tickColor=text_color, domainColor=text_color)),
        y=alt.Y('hydraulic_pressure:Q', scale=alt.Scale(zero=False, padding=10), 
                axis=alt.Axis(title='PRESSURE (BAR)', gridColor=grid_color, labelColor=text_color, titleColor=text_color, tickColor=text_color, domainColor=text_color)),
        color=alt.Color('machine_name:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title="SYSTEM", labelColor=text_color, titleColor=text_color)),
        tooltip=['timestamp:T', 'machine_name:N', 'hydraulic_pressure:Q', 'cycle_state:N']
    ).properties(
        height=320,
        title=alt.TitleParams('GLOBAL PRESSURE OVERVIEW', color='#FFFFFF', font='Segoe UI', fontSize=12, anchor='start')
    ).configure(background=chart_bg).configure_view(strokeWidth=1, stroke='#333333')
    
    return temp_chart, pressure_chart

def main():
    st.title("🏭 HMI SCADA - MULTI-SYSTEM MOLDING NETWORK")
    
    # Sidebar for system selection
    with st.sidebar:
        st.markdown("## 🎛️ CONTROL PANEL")
        
        machines_df = get_machines_cached()
        latest_df = get_latest_readings_nocache()
        
        st.markdown("### SELECT SYSTEM")
        for _, machine in machines_df.iterrows():
            machine_id = machine['machine_id']
            status, icon = get_system_status(latest_df, machine_id)
            
            if st.button(f"{icon} {machine['machine_name']}", key=f"machine_{machine_id}", help=f"Status: {status}"):
                st.session_state.selected_machine = machine_id
        
        st.markdown("---")
        if st.button("🌍 GLOBAL OVERVIEW", key="show_all"):
            st.session_state.selected_machine = None
        
        st.markdown("### SYSTEM SETTINGS")
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
        
        st.session_state.auto_refresh = st.checkbox("🔄 ENABLE REAL-TIME SYNC", value=st.session_state.auto_refresh)
        
        if 'last_update' in st.session_state:
            st.caption(f"LAST SYNC: {st.session_state.last_update}")
    
    # Main content area
    if 'selected_machine' not in st.session_state:
        st.session_state.selected_machine = None
    
    if st.session_state.selected_machine:
        machine_id = st.session_state.selected_machine
        df = get_machine_data_nocache(machine_id, limit=50)
        latest_df = get_latest_readings_nocache()
        alerts_df = get_alerts_nocache(machine_id)
        
        machine_name = f"SYS_{machine_id} - DETAILED TELEMETRY"
        status, icon = get_system_status(latest_df, machine_id)
        
        st.markdown(f"## {icon} {machine_name}")
        
        if status == "NORMAL":
            st.markdown("<div class='status-normal'>SYS STATUS: NOMINAL</div>", unsafe_allow_html=True)
        elif status == "WARNING":
            st.markdown("<div class='status-warning'>SYS STATUS: WARNING DETECTED</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-critical'>SYS STATUS: CRITICAL FAULT</div>", unsafe_allow_html=True)
        
        st.write("") # Spacer
        
        if not latest_df.empty and machine_id in latest_df['machine_id'].values:
            latest = latest_df[latest_df['machine_id'] == machine_id].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("CYCLE PHASE", latest['cycle_state'])
            with col2:
                st.metric("UPPER PLATEN TEMP", f"{latest['platen_temp_upper']:.1f} °C")
            with col3:
                st.metric("HYD PRESSURE", f"{latest['hydraulic_pressure']:.1f} BAR")
            with col4:
                ts = pd.to_datetime(latest['timestamp'], unit='s')
                st.metric("TELEMETRY TS", ts.strftime('%H:%M:%S'))
        
        st.write("") # Spacer
        
        color_scheme = SYSTEM_COLORS.get(machine_id, SYSTEM_COLORS[1])
        temp_chart, pressure_chart = create_optimized_charts(df, machine_id, color_scheme)
        
        if temp_chart and pressure_chart:
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.altair_chart(temp_chart, use_container_width=True)
            with chart_col2:
                st.altair_chart(pressure_chart, use_container_width=True)
        
        if not alerts_df.empty:
            st.markdown("### 🚨 ACTIVE SYSTEM FAULTS")
            st.dataframe(alerts_df.style.map(
                lambda x: 'color: #D50000; font-weight: bold' if x == 'CRITICAL' else 
                       'color: #FFD600; font-weight: bold' if x == 'WARNING' else '', 
                subset=['severity']
            ), use_container_width=True)
        
    else:
        st.markdown("## 🌍 NETWORK OVERVIEW")
        
        alerts_df = get_alerts_nocache()
        critical_count = len(alerts_df[alerts_df['severity'] == 'CRITICAL']) if not alerts_df.empty else 0
        
        if critical_count == 0:
            st.markdown("<div class='status-normal'>NETWORK STATUS: ALL SYSTEMS NOMINAL</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='status-critical'>NETWORK STATUS: {critical_count} CRITICAL FAULTS DETECTED</div>", unsafe_allow_html=True)
        
        st.write("") # Spacer
        
        df = get_machine_data_nocache(limit=100)
        latest_df = get_latest_readings_nocache()
        machines_df = get_machines_cached()
        
        if not machines_df.empty:
            cols = st.columns(3)
            for idx, machine in machines_df.iterrows():
                machine_id = machine['machine_id']
                status, icon = get_system_status(latest_df, machine_id)
                
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"#### {icon} {machine['machine_name']}")
                        if machine_id in latest_df['machine_id'].values:
                            latest = latest_df[latest_df['machine_id'] == machine_id].iloc[0]
                            st.metric("PHASE", latest['cycle_state'])
                            st.metric("TEMP", f"{latest['platen_temp_upper']:.1f} °C")
                            st.metric("PRESS", f"{latest['hydraulic_pressure']:.1f} BAR")
                        else:
                            st.error("NO TELEMETRY")
        
        st.write("") # Spacer
        
        if not df.empty:
            st.markdown("### 📈 AGGREGATED ANALYTICS")
            temp_chart, pressure_chart = create_optimized_overview_charts(df)
            
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.altair_chart(temp_chart, use_container_width=True)
            with chart_col2:
                st.altair_chart(pressure_chart, use_container_width=True)
        
        if not alerts_df.empty:
            st.markdown("### 🚨 GLOBAL FAULT LOG")
            st.dataframe(alerts_df.style.map(
                lambda x: 'color: #D50000; font-weight: bold' if x == 'CRITICAL' else 
                       'color: #FFD600; font-weight: bold' if x == 'WARNING' else '', 
                subset=['severity']
            ), use_container_width=True)
    
    st.session_state.last_update = pd.Timestamp.now().strftime('%H:%M:%S')

    # Auto-refresh logic (Fast relay)
    if st.session_state.get('auto_refresh', True):
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()