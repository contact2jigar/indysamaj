import streamlit as st
import pandas as pd
import requests
import io
import certifi
import urllib.parse
import base64

# --- CONFIGURATION ---
SHEET_ID = "1cCapuxabacizn8FPo1KZ3ynDPRqjdAbqzmnrcAvk2I8"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid="

GIDS = {
    "Center": "1802316304", 
    "Left": "1621742014", 
    "Right": "1180122255",
    "Contacts": "667747417" 
}

st.set_page_config(layout="wide", page_title="American Desi Kaka Chale Vanka", page_icon="🎬")

# --- IMAGE CACHING ---
@st.cache_data
def get_local_img(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# --- CSS STYLING ---
img_base64 = get_local_img("AmericanKakaChaleWaka.jpeg")
if img_base64:
    bg_style = f"background-image: url('data:image/jpeg;base64,{img_base64}');"
else:
    bg_style = "background-color: #111;"

st.markdown(f"""
<style>
[data-testid="column"] {{
    min-width: 0px !important;
    flex: 1 1 0% !important;
}}

[data-testid="stAppViewContainer"]::before {{
    content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    {bg_style} background-size: cover; background-position: center;
    background-repeat: no-repeat; 
    filter: blur(12px) brightness(0.85); /* Increased from 0.65 to 0.85 */
    z-index: -1;
}}

.block-container {{
    background-color: rgba(255, 255, 255, 0.9); padding: 1.5rem !important;
    border-radius: 20px; margin-top: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
}}

.custom-banner {{
    background-color: #333; padding: 10px; border-radius: 12px;
    display: flex; align-items: center; gap: 15px; margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}}
.banner-logo {{ height: 60px !important; width: auto !important; border-radius: 8px; object-fit: contain; }}
.banner-title {{ font-size: 22px; font-weight: bold; color: white; margin: 0; }}
.banner-subtitle {{ font-size: 14px; color: #f1c40f; margin: 0; }}

div[data-testid="stExpander"] {{
    background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("data:image/jpeg;base64,{img_base64}");
    background-size: cover; background-position: center;
    border-radius: 12px !important; border: 1px solid #444 !important;
}}

.bold-label {{ color: #ffffff !important; font-weight: 700; text-shadow: 1px 1px 2px #000; }}

.total-box-compact {{ 
    background: #f1c40f !important; /* Vivid Yellow */
    color: #ffffff !important; 
    text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
    padding: 8px; 
    border-radius: 8px; 
    text-align: center; 
    font-size: 18px; 
    font-weight: 900; 
    height: 42px; 
    display: flex; 
    align-items: center; 
    justify-content: center;
    border: 2px solid #d4ac0d;
}}

/* --- BANNER FIX --- */
.custom-banner {{
    background-color: #333; padding: 10px; border-radius: 12px;
    display: flex; align-items: center; gap: 15px; margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}}
/* Constrain logo height so it doesn't look like a "big banner" */
.banner-logo {{ 
    height: 60px !important; 
    width: auto !important;
    border-radius: 8px; 
    object-fit: contain;
}}
.banner-title {{ font-size: 22px; font-weight: bold; color: white; margin: 0; }}
.banner-subtitle {{ font-size: 14px; color: #f1c40f; margin: 0; }}

/* --- INQUIRY EXPANDER DARK THEME --- */
div[data-testid="stExpander"] {{
    background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("data:image/jpeg;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    border-radius: 12px !important;
    border: 1px solid #444 !important;
}}

[data-testid="stExpanderDetails"] {{
    background-color: rgba(0, 0, 0, 0.3) !important;
    backdrop-filter: blur(4px);
    padding: 20px !important;
    border-radius: 0 0 12px 12px !important;
}}

.bold-label {{ 
    color: #ffffff !important; 
    font-weight: 700;
    text-shadow: 1px 1px 2px #000;
}}

.red-text {{ color: #ff4b4b; font-weight: 800; }}

/* --- 3D SEAT STYLING --- */
.seat {{
    width: 32px; height: 32px; border-radius: 6px; 
    display: flex; flex-direction: column; justify-content: center;
    text-align: center; color: white; font-weight: bold;
    box-shadow: 0 3px 0 rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.3);
    border: 1px solid rgba(0,0,0,0.1);
    transition: transform 0.1s;
    position: relative;
}}
.seat-num {{ font-size: 8px; pointer-events: none; }}
.seat-price {{ font-size: 6px; pointer-events: none; }}
.available {{ background: linear-gradient(180deg, #2ecc71 0%, #27ae60 100%); cursor: default; }}
.sold {{ background: linear-gradient(180deg, #e74c3c 0%, #c0392b 100%); cursor: help; }}

/* --- TOOLTIP --- */
.tooltip-text {{
    visibility: hidden; width: 240px; background-color: #212529; color: #fff; 
    text-align: center; border-radius: 6px; padding: 8px; position: absolute;
    z-index: 100; bottom: 130%; left: 50%; margin-left: -120px; opacity: 0;
    transition: opacity 0.2s; font-size: 11px; border: 1px solid rgba(255,255,255,0.1);
}}
.sold:hover .tooltip-text {{ visibility: visible; opacity: 1; }}

/* --- ACTION BUTTONS --- */
.total-box-compact {{ 
    background: #111827; color: white; padding: 8px; border-radius: 8px; 
    text-align: center; font-size: 16px; font-weight: bold; height: 42px; 
    display: flex; align-items: center; justify-content: center;
}}
.action-button {{
    display: block; padding: 12px; border-radius: 8px; text-align: center;
    font-weight: bold; text-decoration: none; margin-top: 10px; color: white !important; font-size: 14px;
}}
.wa-btn {{ background-color: #25D366; }}
.sms-btn {{ background-color: #007AFF; }}
.disabled-btn {{ background-color: #bdc3c7; pointer-events: none; }}
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
        df = df.dropna(subset=['Name'])
        df['Name'] = df['Name'].astype(str).str.strip()
        df = df[df['Name'].str.lower() != "nan"]
        df = df[df['Name'] != ""]
        names = ["Select Ticket Organizer..."] + list(df['Name'])
        mapping = dict(zip(df['Name'], df['Phone'].astype(str)))
        return names, mapping
    return ["Select Ticket Organizer..."], {}

def get_seat_info(df, sec, row, seat):
    target = f"{sec}{row}{seat:02d}"
    if not df.empty and 'm_id' in df.columns:
        match = df[df['m_id'] == target]
        if not match.empty:
            status_val = str(match.iloc[0].get("Seat_Status","")).lower()
            status = "sold" if "sold" in status_val else "available"
            buyer_name = str(match.iloc[0].get("Buyer_Name", "")).strip()
            if not buyer_name or buyer_name.lower() in ["nan", "none", ""]:
                buyer_name = "Reserved"
            return status, buyer_name
    return "available", ""

def get_price(sec, row):
    return 45 if sec == "C" and row in ["A","B","C","D","E"] else 35

def seat_html(status, num, price, buyer="", full_id=""):
    if status == "sold":
        tooltip_content = f'<span class="tooltip-text">👤 {buyer} &nbsp;|&nbsp; 🎟️ {full_id}</span>'
        return f'<div class="seat sold"><div class="seat-num">{num}</div><div class="seat-price">${price}</div>{tooltip_content}</div>'
    else:
        return f'<div class="seat available"><div class="seat-num">{num}</div><div class="seat-price">${price}</div></div>'

def render_section(section, df):
    rows, seats = list("ABCDEFGHIJKLMN"), (18 if section == "Center" else 4)
    sec_code = section[0]
    html = [f'<tr><td></td><td colspan="{seats + (1 if section == "Center" else 0)}" class="section-header">{section}</td></tr>']
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1, seats + 1):
            status, buyer = get_seat_info(df, sec_code, r, s)
            full_id = f"{section}-{r}{s}"
            row_html += f'<td>{seat_html(status, s, get_price(sec_code, r), buyer, full_id)}</td>'
            if section == "Center" and s == 9:
                row_html += '<td style="width: 20px;"></td>'
        html.append(row_html + '</tr>')
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

def render_full(left, center, right):
    rows = list("ABCDEFGHIJKL")
    ##rows = list("ABCDEFGHIJKLMN")
    html = [
    '<tr>'
    '<td></td>'
    '<td colspan="4" style="text-align:center; font-weight:bold; background:#eee; border-radius:5px;">⬅️ L</td>'
    '<td></td>'
    '<td colspan="19" style="text-align:center; font-weight:bold; background:#eee; border-radius:5px;">🏛️ C</td>'
    '<td></td>'
    '<td colspan="4" style="text-align:center; font-weight:bold; background:#eee; border-radius:5px;">➡️ R</td>'
    '</tr>'
]
    for r in rows:
        row_html = f'<tr><td class="row-label">{r}</td>'
        for s in range(1, 5): 
            status, buyer = get_seat_info(left, "L", r, s)
            full_id = f"Left-{r}{s}"
            row_html += f'<td>{seat_html(status, s, get_price("L", r), buyer, full_id)}</td>'
        row_html += '<td></td>'
        for s in range(1, 19): 
            status, buyer = get_seat_info(center, "C", r, s)
            full_id = f"Center-{r}{s}"
            row_html += f'<td>{seat_html(status, s, get_price("C", r), buyer, full_id)}</td>'
            if s == 9: row_html += '<td style="width: 20px;"></td>'
        row_html += '<td></td>'
        for s in range(1, 5): 
            status, buyer = get_seat_info(right, "R", r, s)
            full_id = f"Right-{r}{s}"
            row_html += f'<td>{seat_html(status, s, get_price("R", r), buyer, full_id)}</td>'
        html.append(row_html + '</tr>')
    return f'<div class="mobile-wrapper"><table class="seat-table">{"".join(html)}</table></div>'

# --- DATA ---
data = {k: load_data(v) for k,v in GIDS.items() if k != "Contacts"}
contact_names, contact_map = get_contacts()

# --- BANNER ---
st.markdown(f"""
<div class="custom-banner">
    <img src="data:image/jpeg;base64,{img_base64}" class="banner-logo">
    <div class="banner-text">
        <p class="banner-title">American Desi Kaka Chale Vanka</p>
        <p class="banner-subtitle">અમેરિકન દેસી કાકા ચાલે વાંકા</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- INQUIRY SECTION ---
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

# --- MAP SECTION ---
t1, t2, t3, t4 = st.tabs(["📍 Map", "⬅️ Left", "🏛️ Center", "➡️ Right"])
with t1: st.markdown(render_full(data["Left"], data["Center"], data["Right"]), unsafe_allow_html=True)
with t2: st.markdown(render_section("Left", data["Left"]), unsafe_allow_html=True)
with t3: st.markdown(render_section("Center", data["Center"]), unsafe_allow_html=True)
with t4: st.markdown(render_section("Right", data["Right"]), unsafe_allow_html=True)

st.divider()
if st.button("🔄 Refresh Seating", use_container_width=True):
    st.cache_data.clear()
    st.rerun()