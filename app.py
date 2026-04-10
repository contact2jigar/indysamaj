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

@st.cache_data
def get_local_img(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# --- UI + CSS ---
bin_str = get_local_img("AmericanKakaChaleWaka.png")
bg_style = f"background-image: url('data:image/png;base64,{bin_str}');" if bin_str else "background-color: #111;"

st.markdown(f"""
<style>
/* Background Image Layer */
[data-testid="stAppViewContainer"]::before {{
    content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    {bg_style} background-size: cover; background-position: center;
    background-repeat: no-repeat; filter: blur(12px) brightness(0.65); z-index: -1;
}}

/* Banner Styling */
.custom-banner {{
    background-color: #333; padding: 15px; border-radius: 12px;
    display: flex; align-items: center; gap: 20px; margin-bottom: 25px;
    border: 1px solid rgba(255,255,255,0.1);
}}
.banner-logo {{ height: 70px; border-radius: 8px; }}
.banner-title {{ font-size: 24px; font-weight: bold; color: white; margin: 0; }}
.banner-subtitle {{ font-size: 18px; color: #f1c40f; margin: 0; }}

/* Glass App Container */
.block-container {{
    background-color: rgba(255, 255, 255, 0.88); padding: 2rem !important;
    border-radius: 20px; margin-top: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
}}

/* Tab & Button Styling */
div[data-baseweb="tab-list"] {{ gap: 2px; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
button[role="tab"] {{
    background-color: #f1f3f6 !important; border-radius: 6px !important;
    padding: 4px 8px !important; font-size: 11px !important;
    font-weight: 600 !important; color: #444 !important; white-space: nowrap;
}}
button[aria-selected="true"] {{ background-color: #111827 !important; color: white !important; }}

@media (max-width:600px){{
    .seat {{ width: 26px !important; height: 26px !important; }}
}}

.mobile-wrapper {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
.seat-table {{ border-spacing: 3px; margin: auto; }}
.seat {{
    width: 32px; height: 32px; border-radius: 6px; 
    display: flex; flex-direction: column; justify-content: center;
    text-align: center; color: white; font-weight: bold;
}}
.seat-num {{ font-size: 9px; }}
.seat-price {{ font-size: 7px; }}
.available {{ background: #2ecc71; }}
.sold {{ background: #e74c3c; }}

.row-label {{ font-weight: bold; font-size: 11px; padding-right: 5px; text-align: right; min-width: 30px; }}
.section-header {{ font-weight: bold; font-size: 12px; text-align: center; }}
.mandatory, .red-text {{ color: #ff0000; font-weight: bold; }}
.fcfs-notice {{ font-weight: bold; font-size: 14px; margin-bottom: 10px; display: block; text-align: center; }}
.map-highlight {{ background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 8px; border: 1px solid #ffeeba; text-align: center; margin-bottom: 15px; font-weight: 500; font-size: 14px; }}
.total-box {{ background: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: center; margin: 10px 0; font-size: 18px; }}

/* Action Buttons */
.action-button {{
    display: block; padding: 12px; border-radius: 8px; text-align: center;
    font-weight: bold; text-decoration: none; margin-top: 10px; color: white !important;
}}
.disabled-btn {{ background-color: #bdc3c7; cursor: not-allowed; pointer-events: none; }}
.wa-btn {{ background-color: #25D366; }}
.sms-btn {{ background-color: #007AFF; }}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
@st.cache_data(ttl=300) 
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
    except: return pd.DataFrame()

def get_contacts():
    df = load_data(GIDS["Contacts"])
    if not df.empty and 'Name' in df.columns and 'Phone' in df.columns:
        return ["Select Ticket Organizer..."] + list(df['Name']), dict(zip(df['Name'], df['Phone'].astype(str)))
    return ["Select Ticket Organizer..."], {}

def get_status(df, sec, row, seat):
    target = f"{sec}{row}{seat:02d}"
    if not df.empty and 'm_id' in df.columns:
        match = df[df['m_id'] == target]
        if not match.empty:
            return "sold" if "sold" in str(match.iloc[0].get("Seat_Status","")).lower() else "available"
    return "available"

def get_price(sec, row):
    return 35 if sec == "C" and row in ["A","B","C","D","E"] else 25

def seat_html(status, num, price):
    return f'<div class="seat {status}"><div class="seat-num">{num}</div><div class="seat-price">${price}</div></div>'

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
    html = ['<tr><td></td><td colspan="3" class="section-header">⬅️ Left</td><td></td><td colspan="18" class="section-header">🏛️ Center</td><td></td><td colspan="3" class="section-header">➡️ Right</td></tr>']
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1,4): row_html += f'<td>{seat_html(get_status(left,"L",r,s),s,get_price("L",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,19): row_html += f'<td>{seat_html(get_status(center,"C",r,s),s,get_price("C",r))}</td>'
        row_html += '<td></td>'
        for s in range(1,4): row_html += f'<td>{seat_html(get_status(right,"R",r,s),s,get_price("R",r))}</td>'
        html.append(row_html + '</tr>')
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

# --- DATA ---
data = {k: load_data(v) for k,v in GIDS.items() if k != "Contacts"}
contact_names, contact_map = get_contacts()

# --- BANNER ---
st.markdown(f"""
<div class="custom-banner">
    <img src="data:image/png;base64,{bin_str}" class="banner-logo">
    <div class="banner-text">
        <p class="banner-title">American Kaka Chale Waka</p>
        <p class="banner-subtitle">અમેરિકન કાકા ચાલે વાકા</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- INQUIRY ---
with st.expander("📩 Send Seat Inquiry Request", expanded=False):
    st.markdown('<span class="fcfs-notice">⚠️ SEATING IS FIRST-COME, FIRST-SERVED BASED</span>', unsafe_allow_html=True)
    
    sender_name = st.text_input("Your Name (Sender)", value="")
    
    st.markdown('Ticket organizer <span class="mandatory">(Mandatory)</span>:', unsafe_allow_html=True)
    selected_person = st.selectbox("label_hidden_contact", contact_names, label_visibility="collapsed")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.write("**Adults**")
        adults = st.number_input("Adults_input", 1, 20, 1, label_visibility="collapsed")
    with col_in2:
        st.markdown('**Kids** <span class="red-text">(Age 10 & Under)</span>', unsafe_allow_html=True)
        child = st.number_input("Kids_input", 0, 20, 0, label_visibility="collapsed")
    
    # Removed default section selection
    section_options = ["Select Section...", "Center VIP (A-E)", "Center (F-N)", "Left", "Right"]
    section = st.selectbox("Section", section_options)
    
    if section != "Select Section...":
        total = adults * (35 if section == "Center VIP (A-E)" else 25)
        st.markdown(f'<div class="total-box">Total Amount: <b>${total}</b></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="total-box" style="color:#666;">Select a section to calculate total</div>', unsafe_allow_html=True)
    
    # Logic for Active vs Disabled buttons based on both selections
    if selected_person != "Select Ticket Organizer..." and section != "Select Section...":
        first_name = selected_person.split()[0]
        phone = contact_map[selected_person].replace("+", "").replace("-", "").replace(" ", "")
        
        msg_text = f"Hi {first_name},\n\nInquiry for American Kaka:\n- Section: {section}\n- Adults: {adults}\n- Kids: {child}\n- Total: ${total}\n\n- From: {sender_name}"
        msg_encoded = urllib.parse.quote(msg_text)
        
        wa_url = f"https://wa.me/{phone}?text={msg_encoded}"
        sms_url = f"sms:{phone};?&body={msg_encoded}"
        
        st.markdown(f'<a href="{wa_url}" target="_blank" class="action-button wa-btn">💬 Send WhatsApp ({first_name})</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="{sms_url}" class="action-button sms-btn">📱 Send Text ({first_name})</a>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="action-button disabled-btn">💬 Send WhatsApp</div>', unsafe_allow_html=True)
        st.markdown('<div class="action-button disabled-btn">📱 Send Text Message</div>', unsafe_allow_html=True)

# --- MAP NOTICE ---
st.markdown('<div class="map-highlight">The seating map below provides a visual overview of available seats. All seating is first-come, first-served.</div>', unsafe_allow_html=True)

# --- TABS ---
t1, t2, t3, t4 = st.tabs(["📍 Map", "⬅️ Left", "🏛️ Center", "➡️ Right"])
with t1: st.markdown(render_full(data["Left"], data["Center"], data["Right"]), unsafe_allow_html=True)
with t2: st.markdown(render_section("Left", data["Left"]), unsafe_allow_html=True)
with t3: st.markdown(render_section("Center", data["Center"]), unsafe_allow_html=True)
with t4: st.markdown(render_section("Right", data["Right"]), unsafe_allow_html=True)

st.divider()
if st.button("🔄 Refresh Seating", use_container_width=True):
    st.cache_data.clear()
    st.rerun()