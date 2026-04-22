import streamlit as st
from supabase import create_client, Client
import cv2
import numpy as np
import pandas as pd
import qrcode
import uuid
from io import BytesIO

# --- CONFIG & CREDENTIALS ---
URL = "https://jaecathvodnrsnbalezj.supabase.co" 
KEY = "sb_publishable_Tlz-QHj4knMEUNuXkd2qGw_EUdhsIzI"

@st.cache_resource
def get_supabase():
    return create_client(URL, KEY)

supabase = get_supabase()

st.set_page_config(page_title="Cloud Attendance", page_icon="⚡")

tab1, tab2, tab3 = st.tabs(["📸 Scan", "📊 Dashboard", "🛠️ Generator"])

# --- TAB 1: SCAN ---
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        img_file = st.camera_input("Scan QR", label_visibility="collapsed")
    with col2:
        manual_id = st.text_input("Manual ID Entry")

    final_id = manual_id if manual_id else None
    if img_file and not final_id:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(frame)
        if data: final_id = data

    if final_id:
        st.success(f"Selected ID: {final_id}")
        if st.button("Confirm Check-in"):
            try:
                # 'check_in' column in your screenshot will auto-fill if set to 'now()'
                # so we only send name and role
                response = supabase.table("attendance").insert({"name": final_id, "role": "Volunteer"}).execute()
                st.balloons()
                st.toast("Success!")
            except Exception as e:
                st.error(f"Insert Failed: {e}")

# --- TAB 2: DASHBOARD (The part that crashed) ---
with tab2:
    st.subheader("Live Logs")
    if st.button("🔄 Refresh"):
        try:
            # Added a try-except here so it doesn't crash your whole app
            res = supabase.table("attendance").select("*").order("check_in", desc=True).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                st.dataframe(df[['name', 'role', 'check_in']], use_container_width=True)
            else:
                st.info("No records found.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.info("Tip: Check if your Supabase RLS policies allow 'Select' for public users.")

# --- TAB 3: GENERATOR ---
with tab3:
    user_name = st.text_input("Volunteer Name")
    if st.button("Generate QR"):
        u_id = str(uuid.uuid4())[:8] # Short unique ID
        img = qrcode.make(u_id)
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption=f"ID: {u_id}")
        st.code(u_id)
            st.warning("No records found in the cloud yet.")
