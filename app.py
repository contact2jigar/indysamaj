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
    "Right": "1180122255",
    "Contacts": "667747417" 
}

st.set_page_config(layout="wide", page_title="American Kaka Chale Waka", page_icon="🎬")

# 🔥 UI + MOBILE FRIENDLY CSS
st.markdown("""
<style>
div[data-baseweb="tab-list"] { gap: 2px; overflow-x: auto; -webkit-overflow-scrolling: touch; }
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

@media (max-width:600px){
    div.stButton > button { font-size: 12px !important; padding: 4px 0px !important; min-height: 30px !important; }
    .seat { width: 26px !important; height: 26px !important; }
}

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

.mandatory, .red-text { color: #ff0000; font-weight: bold; }
.fcfs-notice { font-weight: bold; font-size: 14px; margin-bottom: 10px; display: block; text-align: center; }
.total-box { background: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: center; margin: 10px 0; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

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

# 🔥 Pull list as-is from Google Sheet
def get_contacts():
    df = load_data(GIDS["Contacts"])
    if not df.empty and 'Name' in df.columns and 'Phone' in df.columns:
        # No sorting applied - pulled as listed in sheet
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

# --- DATA LOADING ---
data = {k: load_data(v) for k,v in GIDS.items() if k != "Contacts"}
contact_names, contact_map = get_contacts()

# --- MAIN APP ---
st.title("🎬 American Kaka Chale Waka")

with st.expander("📩 Send Seat Inquiry Request", expanded=False):
    st.markdown('<span class="fcfs-notice">⚠️ SEATING IS FIRST-COME, FIRST-SERVED BASED</span>', unsafe_allow_html=True)
    
    st.markdown('Choose contact <span class="mandatory">(Mandatory)</span>:', unsafe_allow_html=True)
    selected_person = st.selectbox("label_hidden_contact", contact_names, label_visibility="collapsed")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.write("**Adults**")
        adults = st.number_input("Adults_input", min_value=1, max_value=20, value=1, label_visibility="collapsed")
    with col_in2:
        st.markdown('**Kids** <span class="red-text">(Age 10 & Under)</span>', unsafe_allow_html=True)
        child = st.number_input("Kids_input", min_value=0, max_value=20, value=0, label_visibility="collapsed")
    
    section = st.selectbox("Section", ["Center VIP (A-E)", "Center (F-N)", "Left", "Right"])

    unit_price = 35 if section == "Center VIP (A-E)" else 25
    total_amount = adults * unit_price
    
    st.markdown(f'<div class="total-box">Total Amount: <b>${total_amount}</b></div>', unsafe_allow_html=True)
    
    if selected_person != "Select Contact...":
        target_phone = contact_map[selected_person]
        msg = (
            f"Inquiry for American Kaka:\n"
            f"- Section: {section}\n"
            f"- Adults: {adults}\n"
            f"- Children: {child}\n"
            f"- Total: ${total_amount}"
        )
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
        if st.button("📲 Text Request", use_container_width=True):
            st.error("Please select a contact before sending.")

tab_map, tab_l, tab_c, tab_r = st.tabs(["📍 Map", "⬅️ Left", "🏛️ Center", "➡️ Right"])

with tab_map: st.markdown(render_full(data["Left"], data["Center"], data["Right"]), unsafe_allow_html=True)
with tab_l: st.markdown(render_section("Left", data["Left"]), unsafe_allow_html=True)
with tab_c: st.markdown(render_section("Center", data["Center"]), unsafe_allow_html=True)
with tab_r: st.markdown(render_section("Right", data["Right"]), unsafe_allow_html=True)

st.divider()

if st.button("🔄 Refresh Seating", use_container_width=True):
    st.cache_data.clear()
    st.rerun()