import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configure the backend URL
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Video Hub", page_icon="🎥", layout="wide")

st.title("🎥 AI Video Hub")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["View Videos", "Upload Video"])

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
        user_id = st.text_input("User ID (Temporary for testing)", value="test-user")
        
        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])
        
        submit_button = st.form_submit_button("Upload Video")
        
        if submit_button:
            if not title:
                st.warning("Please provide a title.")
            elif not user_id:
                st.warning("Please provide a User ID.")
            elif not uploaded_file:
                st.warning("Please select a video file.")
            else:
                with st.spinner("Uploading video... This may take a while depending on file size."):
                    try:
                        # Prepare the multipart form data
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {'title': title, 'user_id': user_id}
                        
                        response = requests.post(f"{BACKEND_URL}/videos/upload", files=files, data=data)
                        response.raise_for_status()
                        
                        st.success("Video uploaded successfully!")
                        st.json(response.json())
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to upload video. Error: {e}")
                        if hasattr(e, 'response') and e.response is not None:
                            st.error(f"Server response: {e.response.text}")
