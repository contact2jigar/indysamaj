import streamlit as st
import pandas as pd
import requests
import io
import certifi
import urllib.parse
import base64

# CONFIG
SHEET_ID = "1cCapuxabacizn8FPo1KZ3ynDPRqjdAbqzmnrcAvk2I8"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid="

GIDS = {
    "Center": "1802316304", 
    "Left": "1621742014", 
    "Right": "1180122255",
    "Contacts": "667747417" 
}

st.set_page_config(layout="wide", page_title="American Kaka Chale Waka", page_icon="🎬")

# Helper to load local image for the banner logo
def get_local_img(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# --- UI + MOBILE FRIENDLY CSS ---
# Background image logic stays as previously configured with your local file
bin_str = get_local_img("AmericanKakaChaleWaka.png")
bg_style = f"background-image: url('data:image/png;base64,{bin_str}');" if bin_str else "background-color: #111;"

st.markdown(f"""
<style>
/* Background Image Layer */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    {bg_style}
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: blur(12px) brightness(0.65);
    z-index: -1;
}}

/* Banner Styling */
.custom-banner {{
    background-color: #333;
    padding: 15px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 25px;
    border: 1px solid rgba(255,255,255,0.1);
}}
.banner-logo {{
    height: 70px;
    border-radius: 8px;
}}
.banner-text {{
    color: white;
}}
.banner-title {{
    font-size: 24px;
    font-weight: bold;
    margin: 0;
}}
.banner-subtitle {{
    font-size: 18px;
    color: #f1c40f;
    margin: 0;
}}

/* Main App Container */
.block-container {{
    background-color: rgba(255, 255, 255, 0.88);
    padding: 2rem !important;
    border-radius: 20px;
    margin-top: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
}}

div[data-baseweb="tab-list"] {{ gap: 2px; overflow-x: auto; }}
button[role="tab"] {{
    background-color: #f1f3f6 !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #444 !important;
}}
button[aria-selected="true"] {{ background-color: #111827 !important; color: white !important; }}

.mobile-wrapper {{ overflow-x: auto; }}
.seat-table {{ border-spacing: 3px; margin: auto; }}
.seat {{
    width: 32px; height: 32px; border-radius: 6px; 
    display: flex; flex-direction: column; justify-content: center;
    text-align: center; color: white; font-weight: bold;
}}
.available {{ background: #2ecc71; }}
.sold {{ background: #e74c3c; }}

.row-label {{ font-weight: bold; font-size: 11px; padding-right: 5px; text-align: right; }}
.section-header {{ font-weight: bold; font-size: 12px; text-align: center; }}
.total-box {{ background: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: center; font-size: 18px; }}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
@st.cache_data(ttl=2)
def load_data(gid):
    try:
        res = requests.get(f"{BASE_URL}{gid}", verify=certifi.where(), timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^\w]", "", regex=True)
        if gid != GIDS["Contacts"]:
            df = df[df['Row'].isin(list("ABCDEFGHIJKLMN"))]
            if 'Seat_ID' in df.columns:
                df['m_id'] = df['Seat_ID'].astype(str).str.replace(r'[\s-]', '', regex=True).str.upper()
        return df
    except:
        return pd.DataFrame()

def get_contacts():
    df = load_data(GIDS["Contacts"])
    if not df.empty and 'Name' in df.columns and 'Phone' in df.columns:
        contact_dict = dict(zip(df['Name'], df['Phone'].astype(str)))
        return ["Select Contact..."] + list(contact_dict.keys()), contact_dict
    return ["Select Contact..."], {}

def get_status(df, sec, row, seat):
    target = f"{sec}{row}{seat:02d}"
    if not df.empty and 'm_id' in df.columns:
        match = df[df['m_id'] == target]
        if not match.empty:
            val = str(match.iloc[0].get("Seat_Status","")).lower()
            return "sold" if "sold" in val else "available"
    return "available"

def get_price(sec, row):
    return 35 if sec == "C" and row in ["A","B","C","D","E"] else 25

def seat_html(status, num, price):
    return f'<div class="seat {status}"><div style="font-size:9px;">{num}</div><div style="font-size:7px;">${price}</div></div>'

def render_section(section, df):
    rows, seats = list("ABCDEFGHIJKLMN"), (18 if section == "Center" else 3)
    html = [f'<tr><td></td><td colspan="{seats}" class="section-header">{section}</td></tr>']
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1, seats+1):
            row_html += f'<td>{seat_html(get_status(df,section[0],r,s),s,get_price(section[0],r))}</td>'
        html.append(row_html + '</tr>')
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

def render_full(left, center, right):
    rows = list("ABCDEFGHIJKLMN")
    html = ['<tr><td></td><td colspan="3" class="section-header">Left</td><td></td><td colspan="18" class="section-header">Center</td><td></td><td colspan="3" class="section-header">Right</td></tr>']
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1,4): row_html += f'<td>{seat_html(get_status(left,"L",r,s),s,get_price("L",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,19): row_html += f'<td>{seat_html(get_status(center,"C",r,s),s,get_price("C",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,4): row_html += f'<td>{seat_html(get_status(right,"R",r,s),s,get_price("R",r))}</td>'
        html.append(row_html + '</tr>')
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

# --- DATA LOADING ---
data = {k: load_data(v) for k,v in GIDS.items() if k != "Contacts"}
contact_names, contact_map = get_contacts()

# --- CUSTOM BANNER ---
st.markdown(f"""
<div class="custom-banner">
    <img src="data:image/png;base64,{bin_str}" class="banner-logo">
    <div class="banner-text">
        <p class="banner-title">American Kaka Chale Waka</p>
        <p class="banner-subtitle">અમેરિકન કાકા ચાલે વાકા</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- INQUIRY SECTION ---
with st.expander("📩 Send Seat Inquiry Request", expanded=False):
    st.markdown("Choose contact:")
    selected_person = st.selectbox("contact_select", contact_names, label_visibility="collapsed")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        adults = st.number_input("Adults", 1, 20, 1)
    with col_in2:
        child = st.number_input("Kids (10 & Under)", 0, 20, 0)
    
    section_choice = st.selectbox("Section", ["Center VIP (A-E)", "Center (F-N)", "Left", "Right"])
    price = 35 if section_choice == "Center VIP (A-E)" else 25
    total = adults * price
    
    st.markdown(f'<div class="total-box">Total Amount: <b>${total}</b></div>', unsafe_allow_html=True)
    
    if selected_person != "Select Contact...":
        msg = urllib.parse.quote(f"Inquiry for American Kaka:\n- Section: {section_choice}\n- Adults: {adults}\n- Children: {child}\n- Total: ${total}")
        st.markdown(f'<a href="sms:{contact_map[selected_person]}&body={msg}" style="text-decoration:none;"><div style="background:#2ecc71;color:white;padding:12px;border-radius:8px;text-align:center;font-weight:bold;margin-top:10px;">📲 Text Request to {selected_person}</div></a>', unsafe_allow_html=True)

# --- SEATING TABS ---
t1, t2, t3, t4 = st.tabs(["📍 Map", "⬅️ Left", "🏛️ Center", "➡️ Right"])
with t1: st.markdown(render_full(data["Left"], data["Center"], data["Right"]), unsafe_allow_html=True)
with t2: st.markdown(render_section("Left", data["Left"]), unsafe_allow_html=True)
with t3: st.markdown(render_section("Center", data["Center"]), unsafe_allow_html=True)
with t4: st.markdown(render_section("Right", data["Right"]), unsafe_allow_html=True)

st.divider()
if st.button("🔄 Refresh Seating", use_container_width=True):
    st.cache_data.clear()
    st.rerun()