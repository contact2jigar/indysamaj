import streamlit as st
import pandas as pd
import requests
import io
import certifi
import urllib.parse

# CONFIG
SHEET_ID = "1cCapuxabacizn8FPo1KZ3ynDPRqjdAbqzmnrcAvk2I8"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid="

GIDS = {
    "Center": "1802316304", 
    "Left": "1621742014", 
    "Right": "1180122255"
}

# CONTACT LIST
CONTACT_OPTIONS = ["Select Contact..."] + ["Jigar Patel", "Foram Parikh", "Kinjal Tailor"]
CONTACT_MAP = {
    "Jigar Patel": "7174210932",
    "Foram Parikh": "7659781369",
    "Kinjal Tailor": "6155409750"
}

st.set_page_config(layout="wide", page_title="American Kaka Chale Waka", page_icon="🎬")

# 🔥 UI + MOBILE FRIENDLY CSS
st.markdown("""
<style>
/* 🔥 Tabs container */
div[data-baseweb="tab-list"] { gap: 2px; overflow-x: auto; -webkit-overflow-scrolling: touch; }

/* 🔥 Tabs */
button[role="tab"] {
    background-color: #f1f3f6 !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #444 !important;
    white-space: nowrap;
}
button[aria-selected="true"] { background-color: #111827 !important; color: white !important; }

/* 📱 iPhone compact adjustments */
@media (max-width:600px){
    div.stButton > button { font-size: 12px !important; padding: 4px 0px !important; min-height: 30px !important; }
    .seat { width: 26px !important; height: 26px !important; }
    .fcfs-notice { font-size: 12px !important; }
}

/* Seat grid */
.mobile-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.seat-table { border-spacing: 3px; margin: auto; }
.seat {
    width: 32px; height: 32px; border-radius: 6px; 
    display: flex; flex-direction: column; justify-content: center;
    text-align: center; color: white; font-weight: bold;
}
.seat-num { font-size: 9px; }
.seat-price { font-size: 7px; }
.available { background: #2ecc71; }
.sold { background: #e74c3c; }

.row-label { font-weight: bold; font-size: 11px; padding-right: 5px; text-align: right; min-width: 30px; }
.section-header { font-weight: bold; font-size: 12px; text-align: center; }

/* Styling for Labels and Notices */
.mandatory, .red-text { color: #ff0000; font-weight: bold; }
.fcfs-notice { font-weight: bold; font-size: 14px; margin-bottom: 10px; display: block; text-align: center; color: #111827; }
.stExpander { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=2)
def load_data(gid):
    try:
        res = requests.get(f"{BASE_URL}{gid}", verify=certifi.where(), timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^\w]", "", regex=True)
        # Ensure only valid Rows A-N are processed
        df = df[df['Row'].isin(list("ABCDEFGHIJKLMN"))]
        if 'Seat_ID' in df.columns:
            df['m_id'] = df['Seat_ID'].astype(str).str.replace(r'[\s-]', '', regex=True).str.upper()
        return df
    except:
        return pd.DataFrame()

def get_status(df, sec, row, seat):
    target = f"{sec}{row}{seat:02d}"
    if not df.empty and 'm_id' in df.columns:
        match = df[df['m_id'] == target]
        if not match.empty:
            val = str(match.iloc[0].get("Seat_Status","")).lower()
            return "sold" if "sold" in val else "available"
    return "available"

def get_price(sec, row):
    # Center VIP Pricing (Rows A-E)
    return 35 if sec == "C" and row in ["A","B","C","D","E"] else 25

def seat_html(status, num, price):
    return f'<div class="seat {status}"><div class="seat-num">{num}</div><div class="seat-price">${price}</div></div>'

def render_section(section, df):
    rows = list("ABCDEFGHIJKLMN")
    seats = 18 if section == "Center" else 3
    html = [f'<tr><td></td><td colspan="{seats}" class="section-header">{section}</td></tr>']
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1, seats+1):
            row_html += f'<td>{seat_html(get_status(df,section[0],r,s),s,get_price(section[0],r))}</td>'
        row_html += '</tr>'
        html.append(row_html)
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

def render_full(left, center, right):
    rows = list("ABCDEFGHIJKLMN")
    html = ['<tr><td></td><td colspan="3" class="section-header">⬅️ Left</td><td></td><td colspan="18" class="section-header">🏛️ Center</td><td></td><td colspan="3" class="section-header">➡️ Right</td></tr>']
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1,4): row_html += f'<td>{seat_html(get_status(left,"L",r,s),s,get_price("L",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,19): row_html += f'<td>{seat_html(get_status(center,"C",r,s),s,get_price("C",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,4): row_html += f'<td>{seat_html(get_status(right,"R",r,s),s,get_price("R",r))}</td>'
        row_html += '</tr>'
        html.append(row_html)
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

# --- MAIN APP ---
data = {k: load_data(v) for k,v in GIDS.items()}
st.title("🎬 American Kaka Chale Waka")

# 🔥 TOP INQUIRY FORM (CLOSABLE)
with st.expander("📩 Send Seat Inquiry Request", expanded=True):
    st.markdown('<span class="fcfs-notice">⚠️ SEATING IS FIRST-COME, FIRST-SERVED BASED</span>', unsafe_allow_html=True)
    
    st.markdown('Choose contact <span class="mandatory">(Mandatory)</span>:', unsafe_allow_html=True)
    selected_person = st.selectbox("label_hidden_contact", CONTACT_OPTIONS, label_visibility="collapsed")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.write("**Adults**")
        adults = st.number_input("Adults", min_value=1, max_value=20, value=1, label_visibility="collapsed")
    with col_in2:
        st.markdown('**Kids** <span class="red-text">(Age 10 & Under)</span>', unsafe_allow_html=True)
        child = st.number_input("Kids", min_value=0, max_value=20, value=0, label_visibility="collapsed")
    
    section = st.selectbox("Section", ["Center VIP (A-E)", "Center (F-N)", "Left", "Right"])
    
    if selected_person != "Select Contact...":
        target_phone = CONTACT_MAP[selected_person]
        msg = f"Inquiry for American Kaka:\n- Section: {section}\n- Adults: {adults}\n- Children: {child}"
        encoded_msg = urllib.parse.quote(msg)
        sms_url = f"sms:{target_phone}&body={encoded_msg}"
        
        st.markdown(f"""
            <a href="{sms_url}" style="text-decoration: none;">
                <div style="background-color: #2ecc71; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 10px;">
                    📲 Text Request to {selected_person}
                </div>
            </a>
        """, unsafe_allow_html=True)
    else:
        # Dummy button for validation
        if st.button("📲 Text Request", use_container_width=True):
            st.error("Please select a contact from the dropdown above before sending.")

# 🔥 SEATING TABS
tab_map, tab_l, tab_c, tab_r = st.tabs(["📍 Map", "⬅️ Left", "🏛️ Center", "➡️ Right"])

with tab_map: st.markdown(render_full(data["Left"], data["Center"], data["Right"]), unsafe_allow_html=True)
with tab_l: st.markdown(render_section("Left", data["Left"]), unsafe_allow_html=True)
with tab_c: st.markdown(render_section("Center", data["Center"]), unsafe_allow_html=True)
with tab_r: st.markdown(render_section("Right", data["Right"]), unsafe_allow_html=True)

st.divider()

if st.button("🔄 Refresh Seating", use_container_width=True):
    st.cache_data.clear()
    st.rerun()