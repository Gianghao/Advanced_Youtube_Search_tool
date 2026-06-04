import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configure the backend URL
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Video Hub", page_icon="🎥", layout="wide")

st.title("🎥 AI Video Hub")

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configure the backend URL
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Video Hub", page_icon="🎥", layout="wide")

# Initialize session state for user authentication
if 'user' not in st.session_state:
    st.session_state.user = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

st.title("🎥 AI Video Hub")

def logout():
    st.session_state.user = None
    st.session_state.access_token = None
    st.rerun()

# ----------------- AUTHENTICATION -----------------
if not st.session_state.user:
    st.subheader("Authentication")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not email or not password:
                    st.warning("Please fill in both fields.")
                else:
                    with st.spinner("Logging in..."):
                        try:
                            response = requests.post(f"{BACKEND_URL}/auth/signin", json={"email": email, "password": password})
                            response.raise_for_status()
                            data = response.json()
                            st.session_state.user = {
                                "user_id": data["user_id"],
                                "email": data["email"],
                                "username": data["username"]
                            }
                            st.session_state.access_token = data["access_token"]
                            st.success(f"Welcome back, {data['username']}!")
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error("Login failed. Please check your credentials.")
                            if hasattr(e, 'response') and e.response is not None:
                                st.error(f"Details: {e.response.text}")
                                
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username (3-20 chars)")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password (min 6 chars)", type="password")
            register_submit = st.form_submit_button("Register")
            
            if register_submit:
                if not new_email or not new_password or not new_username:
                    st.warning("Please fill in all fields.")
                else:
                    with st.spinner("Registering account..."):
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/auth/signup", 
                                json={"username": new_username, "email": new_email, "password": new_password}
                            )
                            response.raise_for_status()
                            st.success("Registration successful! You can now log in.")
                        except requests.exceptions.RequestException as e:
                            st.error("Registration failed.")
                            if hasattr(e, 'response') and e.response is not None:
                                st.error(f"Details: {e.response.text}")

# ----------------- MAIN APP -----------------
else:
    # Sidebar navigation
    st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.user['username']}**")
    page = st.sidebar.radio("Navigation", ["View Videos", "Upload Video"])
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        logout()

    if page == "View Videos":
        st.header("Uploaded Videos")
        
        with st.spinner("Loading videos..."):
            try:
                response = requests.get(f"{BACKEND_URL}/videos/")
                response.raise_for_status()
                videos = response.json()
                
                if not videos:
                    st.info("No videos found in the database. Upload one to get started!")
                else:
                    # Display videos in a grid
                    cols = st.columns(3)
                    for i, video in enumerate(videos):
                        with cols[i % 3]:
                            st.video(video['video_url'])
                            st.subheader(video['title'])
                            st.caption(f"Uploaded by: {video['user_id']}")
                            
                            # Format timestamp if possible
                            try:
                                dt = datetime.fromisoformat(video['timestamp'])
                                st.caption(f"Date: {dt.strftime('%Y-%m-%d %H:%M')}")
                            except:
                                st.caption(f"Date: {video['timestamp']}")
                            st.divider()
                            
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch videos from backend. Ensure backend is running. Error: {e}")

    elif page == "Upload Video":
        st.header("Upload a New Video")
        
        with st.form("upload_form"):
            title = st.text_input("Video Title", max_chars=100)
            
            # Using the authenticated user's ID automatically
            st.info(f"Uploading as: {st.session_state.user['email']}")
            
            uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])
            
            submit_button = st.form_submit_button("Upload Video")
            
            if submit_button:
                if not title:
                    st.warning("Please provide a title.")
                elif not uploaded_file:
                    st.warning("Please select a video file.")
                else:
                    with st.spinner("Uploading video... This may take a while depending on file size."):
                        try:
                            # Prepare the multipart form data
                            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            data = {
                                'title': title, 
                                'user_id': st.session_state.user['user_id']
                            }
                            
                            response = requests.post(f"{BACKEND_URL}/videos/upload", files=files, data=data)
                            response.raise_for_status()
                            
                            st.success("Video uploaded successfully!")
                            st.json(response.json())
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to upload video. Error: {e}")
                            if hasattr(e, 'response') and e.response is not None:
                                st.error(f"Server response: {e.response.text}")
