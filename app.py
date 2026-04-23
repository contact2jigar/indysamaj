import streamlit as st
import pandas as pd
import requests
import io
import certifi
import urllib.parse
import base64

# --- CONFIGURATION ---
SHEET_ID = "1cCapuxabacizn8FPo1KZ3ynDPRqjdAbqzmnrcAvk2I8"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{{SHEET_ID}}/gviz/tq?tqx=out:csv&gid="

GIDS = {
    "Center": "1802316304", 
    "Left": "1621742014", 
    "Right": "1180122255",
    "Contacts": "667747417" 
}

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title="American Desi Kaka Chale Vanka", page_icon="🎬")

# Helper to load local image for CSS background
def get_local_img(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

img_base64 = get_local_img("AmericanKakaChaleWaka.jpeg")
bg_style = f"""
    background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("data:image/jpeg;base64,{img_base64}");
    background-size: cover;
    background-position: center;
""" if img_base64 else "background-color: #f8f9fa;"

# --- UI STYLING ---
st.markdown(f"""
<style>
    /* General Layout */
    .block-container {{ padding-top: 1rem !important; }}
    [data-testid="stVerticalBlock"] > div {{ gap: 0px !important; }}
    
    /* Inquiry Container with Background Image */
    div[data-testid="stExpander"] {{
        {bg_style}
        border-radius: 12px !important;
        border: 1px solid #ddd !important;
    }}
    
    /* Frosty Glass Overlay */
    [data-testid="stExpanderDetails"] {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(6px);
        padding: 20px !important;
        border-radius: 0 0 12px 12px !important;
    }}

    /* Labels */
    .bold-label {{ 
        font-size: 14px; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
        margin-bottom: 5px; 
        display: block; 
        text-shadow: 1px 1px 3px #000;
    }}

    /* Input Fields */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stNumberInput"] input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #111 !important;
        border: 1px solid #ccc !important;
    }}

    /* Toast Notifications */
    [data-testid="stToast"] {{
        background-color: #1e1e1e !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }}

    /* Action Buttons */
    .action-button {{
        display: block; 
        text-align: center; 
        padding: 12px; 
        border-radius: 8px;
        text-decoration: none; 
        font-weight: bold; 
        margin-top: 10px; 
        color: white !important;
    }}
    .wa-btn {{ background-color: #25D366; box-shadow: 0 3px 0 #128C7E; }}
    .sms-btn {{ background-color: #007AFF; box-shadow: 0 3px 0 #0051a8; }}
    .disabled-btn {{ background-color: #bdc3c7; color: white !important; cursor: not-allowed; pointer-events: none; }}

    /* 3D Seat Styling */
    div.stButton > button {{
        border-radius: 6px !important;
        width: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        line-height: 1.1 !important;
        margin: 2px !important;
        font-size: 10px !important;
        font-weight: bold !important;
        white-space: pre-wrap !important;
        border: 1px solid rgba(0,0,0,0.2) !important;
        box-shadow: 0 3px 0 rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.3) !important;
        transition: all 0.1s ease !important;
    }}
    div.stButton > button[kind="primary"] {{ background: linear-gradient(180deg, #2ecc71 0%, #27ae60 100%) !important; color: white !important; }}
    div.stButton > button[kind="secondary"] {{ background: linear-gradient(180deg, #e74c3c 0%, #c0392b 100%) !important; color: white !important; }}

    .row-label {{ font-weight: bold; font-size: 14px; display: flex; align-items: center; justify-content: center; height: 44px; }}

    /* --- SLIM TITLE BANNER FIX --- */
    .title-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        padding: 10px !important; 
        border-radius: 12px;
        text-align: center;
        margin-bottom: 10px !important;
        border: 1px solid #444;
    }}
    .title-banner h1 {{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.0 !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 8px #000000 !important;
    }}

    /* --- MOBILE HORIZONTAL SCROLL FIX --- */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        width: 100% !important;
        gap: 0px !important;
        padding-bottom: 5px !important;
    }}
    [data-testid="column"] {{
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: min-content !important;
    }}
    /* Clean scrollbar for mobile */
    [data-testid="stHorizontalBlock"]::-webkit-scrollbar {{
        height: 4px;
    }}
    [data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb {{
        background: #888;
        border-radius: 10px;
    }}

</style>
""", unsafe_allow_html=True)

# --- DATA ENGINE ---
@st.cache_data(ttl=300) 
def load_data(gid):
    try:
        res = requests.get(f"{BASE_URL.format(SHEET_ID=SHEET_ID)}{gid}", verify=certifi.where(), timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^\w]", "", regex=True)
        if gid != GIDS["Contacts"] and 'Seat_ID' in df.columns:
            df['m_id'] = df['Seat_ID'].astype(str).str.replace(r'[\s-]', '', regex=True).str.upper()
        return df
    except: return pd.DataFrame()

def get_contacts():
    df = load_data(GIDS["Contacts"])
    if not df.empty and 'Name' in df.columns and 'Phone' in df.columns:
        df = df.dropna(subset=['Name'])
        df = df[df['Name'].astype(str).str.len() > 3]
        names = ["Select Ticket Organizer..."] + list(df['Name'])
        mapping = dict(zip(df['Name'], df['Phone'].astype(str)))
        return names, mapping
    return ["Select Ticket Organizer..."], {}

def get_price(sec, row):
    return "$45" if sec == "C" and row in ["A","B","C","D","E"] else "$35"

def render_seat(col, section_code, row, num, df, tab_name):
    sid_data = f"{section_code}{row}{num:02d}"
    unique_key = f"{tab_name}_{sid_data}"
    price = get_price(section_code, row)
    match = df[df['m_id'] == sid_data] if not df.empty else pd.DataFrame()
    is_sold = not match.empty and "sold" in str(match.iloc[0].get("Seat_Status", "")).lower()
    btn_label = f"{num}\n{price}"
    if is_sold:
        buyer = str(match.iloc[0].get("Buyer_Name", "Unknown"))
        if col.button(btn_label, key=unique_key, type="secondary"):
            # ADDED SEAT NUMBER IN TOAST
            st.toast(f"👤 {buyer} | Seat: {section_code}-{row}{num}", icon="🎟️")
    else:
        col.button(btn_label, key=unique_key, type="primary")

# --- APP START ---
st.markdown(f'''
<div class="title-banner">
    <h1 style="font-size: 26px !important; color: #FFFFFF !important;">
        American Desi Kaka Chale Vanka
    </h1>
    <h1 style="font-size: 22px !important; color: #FFD700 !important; margin-top: 5px !important;">
        અમેરિકન દેસી કાકા ચાલે વાંકા
    </h1>
</div>
''', unsafe_allow_html=True)

contact_names, contact_map = get_contacts()

# --- 📩 INQUIRY SECTION ---
with st.expander("📩 Send Seat Inquiry Request", expanded=True):
    st.markdown('<span class="bold-label">Your Name (Sender)</span>', unsafe_allow_html=True)
    sender_name = st.text_input("sender", value="", label_visibility="collapsed")
    
    st.markdown('<span class="bold-label">Ticket organizer (<span class="red-text">Mandatory</span>):</span>', unsafe_allow_html=True)
    selected_person = st.selectbox("org", contact_names, label_visibility="collapsed")
    
    col_ak1, col_ak2 = st.columns(2)
    with col_ak1:
        st.markdown('<span class="bold-label">Adults</span>', unsafe_allow_html=True)
        adults = st.number_input("A", 1, 20, 1, label_visibility="collapsed")
    with col_ak2:
        st.markdown('<span class="bold-label">Kids (<span class="red-text">Age ≤10 Free</span>)</span>', unsafe_allow_html=True)
        child = st.number_input("K", 0, 20, 0, label_visibility="collapsed")
    
    col_st1, col_st2 = st.columns([2, 1])
    with col_st1:
        st.markdown('<span class="bold-label">Section</span>', unsafe_allow_html=True)
        sec_options = {"Select Section...": 0, "Center VIP (A-E) ($45)": 45, "Center (F-N) ($35)": 35, "Left ($35)": 35, "Right ($35)": 35}
        section_label = st.selectbox("S", list(sec_options.keys()), label_visibility="collapsed")
        price_per_adult = sec_options[section_label]
    with col_st2:
        st.markdown('<span class="bold-label">Total</span>', unsafe_allow_html=True)
        total = adults * price_per_adult if section_label != "Select Section..." else 0
        st.markdown(f'<div class="total-box-compact">${total if total > 0 else "--"}</div>', unsafe_allow_html=True)

    is_ready = selected_person != "Select Ticket Organizer..." and section_label != "Select Section..."
    if is_ready:
        first_name = selected_person.split()[0]
        phone = contact_map[selected_person].replace("+", "").replace("-", "").replace(" ", "")
        msg_text = f"Hi {first_name},\n\nInquiry for American Kaka:\n- Section: {section_label.split(' ($')[0]}\n- Adults: {adults}\n- Kids: {child}\n- Total: ${total}\n\n- From: {sender_name}"
        msg_encoded = urllib.parse.quote(msg_text)
        wa_link, sms_link = f"https://wa.me/{phone}?text={msg_encoded}", f"sms:{phone};?&body={msg_encoded}"
        wa_label, sms_label = f"💬 Send WhatsApp ({first_name})", f"📱 Send Text ({first_name})"
        wa_style, sms_style = "wa-btn", "sms-btn"
    else:
        wa_link = sms_link = "#"
        wa_label, sms_label = "💬 Send WhatsApp", "📱 Send Text"
        wa_style = sms_style = "disabled-btn"

    st.markdown(f'<a href="{wa_link}" target="_blank" class="action-button {wa_style}">{wa_label}</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{sms_link}" class="action-button {sms_style}">{sms_label}</a>', unsafe_allow_html=True)

# --- 🎬 MAP SECTION ---
data = {k: load_data(v) for k,v in GIDS.items() if k != "Contacts"}
#rows = list("ABCDEFGHIJKLMN")
rows = list("ABCDEFGHIJKL")

t1, t2, t3, t4 = st.tabs(["📍 Full Map", "⬅️ Left", "🏛️ Center", "➡️ Right"])

with t1:
    for r in rows:
        cols = st.columns([0.5, 1,1,1,1, 0.4, 1,1,1,1,1,1,1,1,1, 0.2, 1,1,1,1,1,1,1,1,1, 0.4, 1,1,1,1])
        cols[0].markdown(f'<div class="row-label">{r}</div>', unsafe_allow_html=True)
        for s in range(1, 5): render_seat(cols[s], "L", r, s, data["Left"], "f")
        for s in range(1, 10): render_seat(cols[s+5], "C", r, s, data["Center"], "f")
        for s in range(10, 19): render_seat(cols[s+6], "C", r, s, data["Center"], "f")
        for s in range(1, 5): render_seat(cols[s+25], "R", r, s, data["Right"], "f")

with t2:
    for r in rows:
        cols = st.columns([0.5, 1, 1, 1, 1, 15])
        cols[0].markdown(f'<div class="row-label">{r}</div>', unsafe_allow_html=True)
        for s in range(1, 5): render_seat(cols[s], "L", r, s, data["Left"], "l")

with t3:
    for r in rows:
        cols = st.columns([0.5] + [1]*9 + [0.3] + [1]*9)
        cols[0].markdown(f'<div class="row-label">{r}</div>', unsafe_allow_html=True)
        for s in range(1, 10): render_seat(cols[s], "C", r, s, data["Center"], "c")
        for s in range(10, 19): render_seat(cols[s+1], "C", r, s, data["Center"], "c")

with t4:
    for r in rows:
        cols = st.columns([0.5, 1, 1, 1, 1, 15])
        cols[0].markdown(f'<div class="row-label">{r}</div>', unsafe_allow_html=True)
        for s in range(1, 5): render_seat(cols[s], "R", r, s, data["Right"], "r")

st.divider()
if st.button("🔄 Force Refresh"):
    st.cache_data.clear()
    st.rerun()