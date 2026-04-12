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

st.set_page_config(layout="wide", page_title="American Kaka Chale Waka", page_icon="🎬")

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
bin_str = get_local_img("AmericanKakaChaleWaka.png")
bg_style = f"background-image: url('data:image/png;base64,{bin_str}');" if bin_str else "background-color: #111;"

st.markdown(f"""
<style>
[data-testid="column"] {{
    min-width: 0px !important;
    flex: 1 1 0% !important;
}}

[data-testid="stAppViewContainer"]::before {{
    content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    {bg_style} background-size: cover; background-position: center;
    background-repeat: no-repeat; filter: blur(12px) brightness(0.65); z-index: -1;
}}

.block-container {{
    background-color: rgba(255, 255, 255, 0.9); padding: 1.5rem !important;
    border-radius: 20px; margin-top: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
}}

.custom-banner {{
    background-color: #333; padding: 12px; border-radius: 12px;
    display: flex; align-items: center; gap: 15px; margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}}
.banner-logo {{ height: 55px; border-radius: 8px; }}
.banner-title {{ font-size: 20px; font-weight: bold; color: white; margin: 0; }}
.banner-subtitle {{ font-size: 14px; color: #f1c40f; margin: 0; }}

.mini-label {{ font-size: 11px; font-weight: bold; margin-bottom: 2px; display: block; color: #444; }}

.mobile-wrapper {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
.seat-table {{ border-spacing: 2px; margin: auto; }}
.seat {{
    width: 28px; height: 28px; border-radius: 5px; 
    display: flex; flex-direction: column; justify-content: center;
    text-align: center; color: white; font-weight: bold;
}}
.seat-num {{ font-size: 8px; }}
.seat-price {{ font-size: 6px; }}
.available {{ background: #2ecc71; }}
.sold {{ background: #e74c3c; }}

.row-label {{ font-weight: bold; font-size: 10px; padding-right: 4px; text-align: right; }}
.section-header {{ font-weight: bold; font-size: 11px; text-align: center; }}

.payment-box {{ background-color: #d4edda; color: #155724; padding: 10px; border-radius: 8px; border: 1px solid #c3e6cb; margin: 10px 0; font-size: 12px; }}
.total-box-compact {{ 
    background: #111827; color: white; padding: 8px; border-radius: 8px; 
    text-align: center; font-size: 16px; font-weight: bold; height: 42px; 
    display: flex; align-items: center; justify-content: center;
}}

.action-button {{
    display: block; padding: 12px; border-radius: 8px; text-align: center;
    font-weight: bold; text-decoration: none; margin-top: 10px; color: white !important; font-size: 14px;
}}
.disabled-btn {{ background-color: #bdc3c7; cursor: not-allowed; }}
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
    # Updated prices: 45 for VIP, 35 for Standard
    return 45 if sec == "C" and row in ["A","B","C","D","E"] else 35

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
    html = ['<tr><td></td><td colspan="3" class="section-header">⬅️ L</td><td></td><td colspan="18" class="section-header">🏛️ C</td><td></td><td colspan="3" class="section-header">➡️ R</td></tr>']
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

# --- INQUIRY SECTION ---
with st.expander("📩 Send Seat Inquiry Request", expanded=True):
    
    sender_name = st.text_input("Your Name (Sender)", value="")
    
    # Updated Label: Mandatory in Red and Bold
    st.markdown('<span class="mini-label">Ticket organizer (<span style="color:red; font-weight:bold;">Mandatory</span>):</span>', unsafe_allow_html=True)
    selected_person = st.selectbox("org", contact_names, label_visibility="collapsed")
    
    col_ak1, col_ak2 = st.columns(2)
    with col_ak1:
        st.markdown('<span class="mini-label">Adults</span>', unsafe_allow_html=True)
        adults = st.number_input("A", 1, 20, 1, label_visibility="collapsed")
    with col_ak2:
        # Updated Label: Kids Age Free in Red and Bold
        st.markdown('<span class="mini-label">Kids (<span style="color:red; font-weight:bold;">Age ≤10 Free</span>)</span>', unsafe_allow_html=True)
        child = st.number_input("K", 0, 20, 0, label_visibility="collapsed")
    
    col_st1, col_st2 = st.columns([2, 1])
    with col_st1:
        st.markdown('<span class="mini-label">Section</span>', unsafe_allow_html=True)
        # Updated Dropdown with 45 and 35 prices
        sec_options = {
            "Select Section...": 0,
            "Center VIP (A-E) ($45)": 45,
            "Center (F-N) ($35)": 35,
            "Left ($35)": 35,
            "Right ($35)": 35
        }
        section_label = st.selectbox("S", list(sec_options.keys()), label_visibility="collapsed")
        price_per_adult = sec_options[section_label]
        
    with col_st2:
        st.markdown('<span class="mini-label">Total</span>', unsafe_allow_html=True)
        if section_label != "Select Section...":
            total = adults * price_per_adult
            st.markdown(f'<div class="total-box-compact">${total}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="total-box-compact" style="font-size:12px; color:#666;">--</div>', unsafe_allow_html=True)

    if section_label != "Select Section...":
        st.markdown(
            '<div class="payment-box">'
            '<b>💳 Payment:</b> Please Zelle the total to the selected organizer’s phone number after sending request.'
            '</div>',
            unsafe_allow_html=True
        )

    if selected_person != "Select Ticket Organizer..." and section_label != "Select Section...":
        first_name = selected_person.split()[0]
        phone = contact_map[selected_person].replace("+", "").replace("-", "").replace(" ", "")
        
        clean_section = section_label.split(" ($")[0]
        msg_text = f"Hi {first_name},\n\nInquiry for American Kaka:\n- Section: {clean_section}\n- Adults: {adults}\n- Kids: {child}\n- Total: ${total}\n\n- From: {sender_name}"
        msg_encoded = urllib.parse.quote(msg_text)
        
        st.markdown(f'<a href="https://wa.me/{phone}?text={msg_encoded}" target="_blank" class="action-button wa-btn">💬 Send WhatsApp ({first_name})</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="sms:{phone};?&body={msg_encoded}" class="action-button sms-btn">📱 Send Text ({first_name})</a>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="action-button disabled-btn">Select Organizer & Section</div>', unsafe_allow_html=True)

# --- MAP SECTION ---
st.markdown('<div style="background:#fff3cd; padding:8px; border-radius:8px; font-size:12px; text-align:center; margin-bottom:10px; color:#856404; font-weight:500;">The map below shows available seats. First-come, first-served.</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📍 Map", "⬅️ Left", "🏛️ Center", "➡️ Right"])
with t1: st.markdown(render_full(data["Left"], data["Center"], data["Right"]), unsafe_allow_html=True)
with t2: st.markdown(render_section("Left", data["Left"]), unsafe_allow_html=True)
with t3: st.markdown(render_section("Center", data["Center"]), unsafe_allow_html=True)
with t4: st.markdown(render_section("Right", data["Right"]), unsafe_allow_html=True)

st.divider()
if st.button("🔄 Refresh Seating", use_container_width=True):
    st.cache_data.clear()
    st.rerun()