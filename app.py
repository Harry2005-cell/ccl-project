import streamlit as st
from st_supabase_connection import SupabaseConnection
import cv2
import pandas as pd
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Cloud Attendance", page_icon="☁️", layout="centered")

# --- UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007BFF; color: white; }
    .status-box { padding: 20px; border-radius: 10px; border: 1px solid #ddd; background: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CLOUD CONNECTION ---
# Fill these in your .streamlit/secrets.toml or Streamlit Cloud Secrets
conn = st.connection("supabase", type=SupabaseConnection)

def log_attendance(name):
    """Inserts a new record into the Supabase cloud table."""
    try:
        data = conn.table("attendance").insert({"name": name, "role": "Volunteer"}).execute()
        return True
    except Exception as e:
        st.error(f"Error logging to cloud: {e}")
        return False

# --- USER INTERFACE ---
st.title("☁️ Smart Cloud Attendance")
st.write("Scan your QR code to check in instantly.")

tabs = st.tabs(["📸 Scanner", "📊 Live Dashboard"])

with tabs[0]:
    st.subheader("QR Scanner")
    img_file_buffer = st.camera_input("Align QR code in frame")

    if img_file_buffer:
        # Process the image from camera
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(pd.np.frombuffer(bytes_data, pd.np.uint8), cv2.IMREAD_COLOR)
        
        # Detect QR Code
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(cv2_img)

        if data:
            st.success(f"Verified: {data}")
            if st.button(f"Confirm Check-in for {data}"):
                if log_attendance(data):
                    st.balloons()
                    st.info(f"Check-in recorded at {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.warning("No QR code detected. Please try again.")

with tabs[1]:
    st.subheader("Real-time Attendance Logs")
    if st.button("Refresh Data"):
        # Fetch data from Supabase
        response = conn.table("attendance").select("*").order("check_in", desc=True).execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Simple Metric
            st.metric("Total Check-ins Today", len(df))
        else:
            st.write("No logs found for today.")