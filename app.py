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
    .stButton>button { 
        background: linear-gradient(45deg, #007cf0, #00dfd8); 
        color: white; border: none; font-weight: bold; width: 100%; border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Cloud Attendance")

tab1, tab2, tab3 = st.tabs(["📸 Scan & Check-in", "📊 Dashboard", "🛠️ QR Generator"])

# --- TAB 1: SCANNING ---
with tab1:
    st.subheader("Check-in Portal")
    col1, col2 = st.columns([2, 1])
    with col1:
        img_file = st.camera_input("Scan QR Code")
    with col2:
        manual_id = st.text_input("OR Manual ID")

    final_id = None
    if img_file:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(frame)
        if data:
            final_id = data
            st.success(f"QR Scanned: {final_id}")
    
    if manual_id:
        final_id = manual_id

    if final_id:
        if st.button("Confirm Check-in"):
            try:
                entry = {"name": final_id, "role": "Authorized User"}
                supabase.table("attendance").insert(entry).execute()
                st.balloons()
                st.toast("Success!", icon="✅")
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.subheader("Live Attendance Logs")
    if st.button("🔄 Refresh Data"):
        try:
            res = supabase.table("attendance").select("*").order("check_in", desc=True).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                if 'check_in' in df.columns:
                    df['check_in'] = pd.to_datetime(df['check_in']).dt.strftime('%Y-%m-%d %H:%M')
                    st.dataframe(df[['name', 'role', 'check_in']], use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.warning("No records found in the cloud yet.")
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

# --- TAB 3: GENERATOR ---
with tab3:
    st.subheader("Generate Unique ID QR")
    user_label = st.text_input("Name/Label")
    if st.button("Generate Unique QR"):
        unique_id = str(uuid.uuid4())[:8].upper()
        qr_img = qrcode.make(unique_id)
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.divider()
        st.image(byte_im, width=250)
        st.code(f"ID: {unique_id}")
        st.download_button(
            label="💾 Download QR Code",
            data=byte_im,
            file_name=f"qr_{unique_id}.png",
            mime="image/png"
        )
