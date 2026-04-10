import streamlit as st
import pandas as pd
import requests
import io
import certifi

# CONFIG
SHEET_ID = "1cCapuxabacizn8FPo1KZ3ynDPRqjdAbqzmnrcAvk2I8"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid="

GIDS = {
    "Center": "1802316304", 
    "Left": "1621742014", 
    "Right": "1180122255"
}

st.set_page_config(layout="wide", page_title="American Kaka Chale Waka", page_icon="🎬")

# 🔥 UI + MOBILE FRIENDLY CSS
st.markdown("""
<style>

/* 🔥 Tabs container */
div[data-baseweb="tab-list"] {
    gap: 2px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

/* 🔥 Tabs */
button[role="tab"] {
    background-color: #f1f3f6 !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #444 !important;
    white-space: nowrap;
}

/* 🔥 Active tab */
button[aria-selected="true"] {
    background-color: #111827 !important;
    color: white !important;
}

/* 📱 iPhone compact - even smaller for mobile */
@media (max-width:600px){
    button[role="tab"] {
        padding: 4px 6px !important;
        font-size: 11px !important;
    }
    
    /* Shrink the Streamlit Refresh button font */
    div.stButton > button {
        font-size: 12px !important;
        padding: 4px 0px !important;
        min-height: 30px !important;
    }
}

/* Seat grid */
.mobile-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.seat-table { border-spacing: 3px; margin: auto; }

.seat {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    color: white;
    font-weight: bold;
}

.seat-num { font-size: 9px; }
.seat-price { font-size: 7px; }

.available { background: #2ecc71; }
.sold { background: #e74c3c; }

.row-label {
    font-weight: bold;
    font-size: 11px;
    padding-right: 5px;
    text-align: right;
    min-width: 30px;
}

.section-header {
    font-weight: bold;
    font-size: 12px;
    text-align: center;
}

@media (max-width:600px){
    .seat { width: 26px; height: 26px; }
    .seat-num { font-size: 8px; }
    .seat-price { font-size: 6px; }
}

</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=2)
def load_data(gid):
    try:
        res = requests.get(f"{BASE_URL}{gid}", verify=certifi.where(), timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^\w]", "", regex=True)
        df = df.dropna(subset=[df.columns[0]])
        if 'Seat_ID' in df.columns:
            df['m_id'] = df['Seat_ID'].astype(str).str.replace(r'[\s-]', '', regex=True).str.upper()
        return df
    except:
        return pd.DataFrame()

def get_status(df, sec, row, seat):
    target = f"{sec}{row}{seat:02d}"
    if not df.empty:
        match = df[df['m_id'] == target]
        if not match.empty:
            val = str(match.iloc[0].get("Seat_Status","")).lower()
            if "sold" in val:
                return "sold"
    return "available"

def get_price(sec, row):
    if sec == "C" and row in ["A","B","C","D","E"]:
        return 35
    return 25

def seat_html(status, num, price):
    return f"""
    <div class="seat {status}">
        <div class="seat-num">{num}</div>
        <div class="seat-price">${price}</div>
    </div>
    """

def render_section(section, df):
    rows = list("ABCDEFGHIJKLMN")
    seats = 18 if section == "Center" else 3
    html = []
    html.append(f'<tr><td></td><td colspan="{seats}" class="section-header">{section}</td></tr>')
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1, seats+1):
            row_html += f'<td>{seat_html(get_status(df,section[0],r,s),s,get_price(section[0],r))}</td>'
        row_html += '</tr>'
        html.append(row_html)
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

def render_full(left, center, right):
    rows = list("ABCDEFGHIJKLMN")
    html = []
    html.append("""
    <tr>
        <td></td>
        <td colspan="3" class="section-header">⬅️ Left</td>
        <td></td>
        <td colspan="18" class="section-header">🏛️ Center</td>
        <td></td>
        <td colspan="3" class="section-header">➡️ Right</td>
    </tr>
    """)
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1,4):
            row_html += f'<td>{seat_html(get_status(left,"L",r,s),s,get_price("L",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,19):
            row_html += f'<td>{seat_html(get_status(center,"C",r,s),s,get_price("C",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,4):
            row_html += f'<td>{seat_html(get_status(right,"R",r,s),s,get_price("R",r))}</td>'
        row_html += '</tr>'
        html.append(row_html)
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

# LOAD DATA
data = {k: load_data(v) for k,v in GIDS.items()}

st.title("🎬 American Kaka Chale Waka")

# 🔥 TABS
tab_map, tab_l, tab_c, tab_r = st.tabs([
    "📍 Map",
    "⬅️ Left",
    "🏛️ Center",
    "➡️ Right"
])

with tab_map:
    st.markdown(render_full(data["Left"], data["Center"], data["Right"]), unsafe_allow_html=True)

with tab_l:
    st.markdown(render_section("Left", data["Left"]), unsafe_allow_html=True)

with tab_c:
    st.markdown(render_section("Center", data["Center"]), unsafe_allow_html=True)

with tab_r:
    st.markdown(render_section("Right", data["Right"]), unsafe_allow_html=True)

st.divider()

if st.button("🔄 Refresh Seating", use_container_width=True):
    st.cache_data.clear()
    st.rerun()