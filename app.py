import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import certifi

# ========================================================
# 📥 DATA CONFIGURATION
# ========================================================
SHEET_ID = "1cCapuxabacizn8FPo1KZ3ynDPRqjdAbqzmnrcAvk2I8"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

GIDS = {
    "Center": "1802316304", 
    "Left": "1621742014", 
    "Right": "1180122255", 
    "Config": "401984418" 
}

@st.cache_data(ttl=60)
def load_tab(gid):
    try:
        url = f"{BASE_URL}&gid={gid}"
        res = requests.get(url, verify=certifi.where(), timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how='all')
        if 'Seat_ID' in df.columns:
            df['m_id'] = df['Seat_ID'].astype(str).str.replace(r'[\s-]', '', regex=True).str.upper()
        return df
    except:
        return pd.DataFrame()

# ========================================================
# 🗺️ SECTIONED MAP GENERATOR
# ========================================================
def generate_sectioned_map(config_df, live_data_dict):
    all_seats = []
    row_labels = [] 
    
    # Ignore empty footer rows in SeatConfig
    valid_config = config_df.dropna(subset=['Section Name', 'Seats/Row'])
    
    for _, cfg in valid_config.iterrows():
        try:
            sec_full = str(cfg['Section Name'])      
            main_sec = sec_full.split('-')[0].strip()
            num_rows = int(float(cfg['Rows']))
            seats_per = int(float(cfg['Seats/Row']))
            start_row = str(cfg['Start Row']).strip().upper()
            
            live_df = live_data_dict.get(main_sec, pd.DataFrame())
            
            for r_offset in range(num_rows):
                row_char = chr(ord(start_row) + r_offset)
                
                # Determine label placement based on section
                if main_sec == "Left": x_base = 1 - 35
                elif main_sec == "Right": x_base = 1 + 25
                else: x_base = 1 - 12.5
                
                # Row Label (e.g., "A", "F", "J")
                row_labels.append({"x": x_base - 2, "y": -(ord(row_char) - 64), "text": row_char})

                for s in range(1, seats_per + 1):
                    y_pos = -(ord(row_char) - 64)
                    if main_sec == "Left": x_pos = s - 35
                    elif main_sec == "Right": x_pos = s + 25
                    else: x_pos = s - 12.5
                    
                    m_id = f"{main_sec[0]}{s}{row_char}".upper()
                    status = "Available"
                    
                    if not live_df.empty:
                        match = live_df[live_df['m_id'] == m_id]
                        if not match.empty:
                            raw_s = str(match.iloc[0]['Seat Status']).strip().lower()
                            status = "Sold" if raw_s in ["sold", "pending"] else "Available"
                        else:
                            status = "Missing"

                    all_seats.append({
                        "Section": sec_full,
                        "Row": row_char,
                        "Seat": s,
                        "Status": status,
                        "Label": str(s), # Seat number label
                        "x": x_pos,
                        "y": y_pos
                    })
        except:
            continue 

    return pd.DataFrame(all_seats), pd.DataFrame(row_labels).drop_duplicates()

# ========================================================
# 🚀 STREAMLIT APP
# ========================================================
st.set_page_config(layout="wide")
st.title("🎟️ Auditorium Live Seating")

config_data = load_tab(GIDS["Config"])
live_tabs = {s: load_tab(GIDS[s]) for s in ["Center", "Left", "Right"]}

if not config_data.empty:
    map_df, labels_df = generate_sectioned_map(config_data, live_tabs)
    
    if not map_df.empty:
        # Create map with Seat Numbers (text mode)
        fig = px.scatter(
            map_df, x="x", y="y", color="Status",
            text="Label", # Displays the seat number on the square
            hover_data={"x":False, "y":False, "Section":True, "Row":True, "Seat":True, "Label":False},
            color_discrete_map={"Available": "#2ecc71", "Sold": "#95a5a6", "Missing": "#e74c3c"}
        )
        
        # Add Row Labels (A-Z)
        for _, lbl in labels_df.iterrows():
            fig.add_annotation(
                x=lbl['x'], y=lbl['y'], text=lbl['text'],
                showarrow=False, font=dict(size=14, color="black", family="Arial Black"),
                xanchor="right"
            )
        
        # Style the seat squares and numbers
        fig.update_traces(
            marker=dict(size=22, symbol='square'),
            textfont=dict(size=9, color="white"), # Small white text for seat numbers
            textposition="middle center"
        )
        
        fig.update_layout(
            xaxis_visible=False, 
            yaxis_visible=False, 
            height=850,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary Metrics
        st.divider()
        cols = st.columns(3)
        for i, name in enumerate(["Left", "Center", "Right"]):
            count = len(map_df[(map_df['Section'].str.contains(name)) & (map_df['Status'] == "Available")])
            cols[i].metric(f"{name} Available", count)
            
else:
    st.error("Missing SeatConfig. Verify GID 401984418.")

if st.button("🔄 Sync Live Status"):
    st.cache_data.clear()
    st.rerun()