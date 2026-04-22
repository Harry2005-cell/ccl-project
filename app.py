import streamlit as st
from supabase import create_client, Client
import cv2
import numpy as np
import pandas as pd
import qrcode
import uuid
from io import BytesIO
from datetime import datetime

# --- CONFIG & CREDENTIALS ---
# Ensure these match your Supabase Dashboard -> Settings -> API
URL = "https://jaecathvodnrsnbalezj.supabase.co" 
KEY = "sb_publishable_Tlz-QHj4knMEUNuXkd2qGw_EUdhsIzI"

@st.cache_resource
def get_supabase():
    return create_client(URL, KEY)

supabase = get_supabase()

# --- UI SETTINGS ---
st.set_page_config(page_title="Cloud Attendance Pro", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .main-card { background: #1E1E1E; padding: 25px; border-radius: 15px; border: 1px solid #333; }
    .stButton>button { 
        background: linear-gradient(45deg, #007cf0, #00dfd8); 
        color: white; 
        border: none; 
        font-weight: bold; 
        width: 100%;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP LOGIC ---
st.title("⚡ Cloud Attendance")
st.write("Secure, Real-time Check-in System")

tab1, tab2, tab3 = st.tabs(["📸 Scan & Check-in", "📊 Dashboard", "🛠️ QR Generator"])

# --- TAB 1: SCANNING & MANUAL ENTRY ---
with tab1:
    st.subheader("Check-in Portal")
    
    # Create two columns for Scan vs Manual
    col1, col2 = st.columns([2, 1])
    
    with col1:
        img_file = st.camera_input("Scan QR Code", label_visibility="visible")
    
    with col2:
        manual_id = st.text_input("OR Manual ID", placeholder="Enter ID here...")

    # Logic to capture the ID
    final_id = None
    
    # 1. Check if a QR was scanned
    if img_file:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(frame)
        if data:
            final_id = data
            st.success(f"QR Scanned: **{final_id}**")
    
    # 2. Overwrite with manual ID if typed
    if manual_id:
        final_id = manual_id
        st.info(f"Using Manual ID: **{final_id}**")

    if final_id:
        if st.button("Confirm Check-in"):
            try:
                # Insert into Supabase (Matches your table columns: name, role)
                entry = {"name": final_id, "role": "Authorized User"}
                response = supabase.table("attendance").insert(entry).execute()
                
                st.balloons()
                st.toast(f"Logged: {final_id}", icon="✅")
            except Exception as e:
                st.error(f"Database Error: {e}")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.subheader("Live Attendance Logs")
    if st.button("🔄 Refresh Data"):
        try:
            res = supabase.table("attendance").select("*").order("check_in", desc=True).execute()
            
            if res.data:
                df = pd.DataFrame(res.data)
                # Ensure the column names match your Supabase table
                if 'check_in' in df.columns:
                    df['check_in'] = pd.to_datetime(df['check_in']).dt.strftime('%Y-%m-%d %H:%M')
                    st.dataframe(df[['name', 'role', 'check_in']], use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.warning("No records found in the cloud yet.")
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

# --- TAB 3: QR GENERATOR ---
with tab3:
    st.subheader("Generate Unique ID QR")
    user_label = st.text_input("Name/Label for this QR", placeholder="Volunteer Name")
    
    if st.button("Generate Unique QR"):
        # Create a unique 8-character ID
        unique_id = str(uuid.uuid4())[:8].upper()
        
        # Generate QR
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(unique_id)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Buffer to display/download
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.divider()
        st.success(f"Generated ID: **{unique_id}**")
        st.image(byte_im, width=250)
        st.download_button(
            label="💾 Download QR Code",
            data=byte_im,
            file_name=f"qr_{unique_id}.png",
            mime="image/png"
        )loud yet.")
