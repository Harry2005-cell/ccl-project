import streamlit as st
from supabase import create_client, Client
import cv2
import numpy as np
import pandas as pd
from datetime import datetime

# --- CONFIG & CREDENTIALS ---
# Replace these with your actual Supabase "Project URL" and "anon public key"
URL = "https://jaecathvodnrsnbalezj.supabase.co" 
KEY = "sb_publishable_Tlz-QHj4knMEUNuXkd2qGw_EUdhsIzI"

# Initialize Supabase Client
@st.cache_resource
def get_supabase():
    return create_client(URL, KEY)

supabase = get_supabase()

# --- UI SETTINGS ---
st.set_page_config(page_title="Cloud Attendance", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .main-card { background: #1E1E1E; padding: 25px; border-radius: 15px; border: 1px solid #333; }
    .stButton>button { background: linear-gradient(45deg, #007cf0, #00dfd8); color: white; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- APP LOGIC ---
st.title("⚡ Cloud Attendance")
st.write("Secure, Real-time Check-in System")

tab1, tab2 = st.tabs(["📸 Scan QR", "📊 Dashboard"])

with tab1:
    st.subheader("Point Camera at QR Code")
    img_file = st.camera_input("Scan", label_visibility="collapsed")

    if img_file:
        # Convert image to OpenCV format
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        
        # QR Detection
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(frame)

        if data:
            st.success(f"Identified: **{data}**")
            if st.button("Confirm Check-in"):
                # Insert into Supabase
                entry = {"name": data, "role": "Volunteer"}
                response = supabase.table("attendance").insert(entry).execute()
                
                if response:
                    st.balloons()
                    st.toast("Attendance Logged Successfully!", icon="✅")
        else:
            st.info("Searching for QR code...")

with tab2:
    st.subheader("Live Attendance Logs")
    if st.button("🔄 Refresh Data"):
        # Fetch from Supabase
        res = supabase.table("attendance").select("*").order("check_in", desc=True).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            # Formatting the date for the UI
            df['check_in'] = pd.to_datetime(df['check_in']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df[['name', 'role', 'check_in']], use_container_width=True)
        else:
            st.warning("No records found in the cloud yet.")