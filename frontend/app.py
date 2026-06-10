import streamlit as st
import requests
from datetime import datetime

# Configure the backend URL
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Video Hub",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Search result cards */
.result-card {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
    border: 1px solid #3a3a5c;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.result-card:hover {
    transform: translateY(-2px);
    border-color: #7c6af7;
}
.result-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e2e2f0;
    margin-bottom: 4px;
}
.result-meta {
    font-size: 0.85rem;
    color: #888;
}
.similarity-badge {
    display: inline-block;
    background: linear-gradient(90deg, #7c6af7, #a855f7);
    color: white;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 600;
}
.status-processing {
    background: #f59e0b22;
    color: #f59e0b;
    border: 1px solid #f59e0b55;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-ready {
    background: #10b98122;
    color: #10b981;
    border: 1px solid #10b98155;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'playing_video' not in st.session_state:
    st.session_state.playing_video = None  # {"url": str, "start_time": int, "title": str}
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = None


def logout():
    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.playing_video = None
    st.session_state.search_query = ""
    st.session_state.search_results = None
    st.rerun()


def format_timestamp(seconds: float) -> str:
    """Format seconds → MM:SS."""
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def status_badge(status: str) -> str:
    if status == "processing":
        return '<span class="status-processing">⏳ Processing</span>'
    elif status == "ready":
        return '<span class="status-ready">✅ Ready</span>'
    else:
        return f'<span style="color:#888">{status}</span>'


# ===================== AUTHENTICATION =====================
if not st.session_state.user:
    st.markdown("## 🎥 AI Video Hub")
    st.markdown("Smart AI-powered video content semantic search system")
    st.divider()
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if not email or not password:
                    st.warning("Please fill in all fields.")
                else:
                    with st.spinner("Logging in..."):
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/auth/signin",
                                json={"email": email, "password": password}
                            )
                            response.raise_for_status()
                            data = response.json()
                            st.session_state.user = {
                                "user_id": data["user_id"],
                                "email": data["email"],
                                "username": data["username"],
                            }
                            st.session_state.access_token = data["access_token"]
                            st.success(f"Welcome back, {data['username']}!")
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error("Login failed. Please check your credentials.")
                            if hasattr(e, "response") and e.response is not None:
                                st.error(f"Details: {e.response.text}")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username (3-20 characters)")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password (min 6 characters)", type="password")
            register_submit = st.form_submit_button("Register", use_container_width=True)

            if register_submit:
                if not new_email or not new_password or not new_username:
                    st.warning("Please fill in all fields.")
                else:
                    with st.spinner("Registering..."):
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/auth/signup",
                                json={"username": new_username, "email": new_email, "password": new_password},
                            )
                            response.raise_for_status()
                            st.success("Registration successful! You can log in now.")
                        except requests.exceptions.RequestException as e:
                            st.error("Registration failed.")
                            if hasattr(e, "response") and e.response is not None:
                                st.error(f"Details: {e.response.text}")

# ===================== MAIN APP =====================
else:
    user = st.session_state.user

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown(f"### 👤 {user['username']}")
        st.caption(user["email"])
        st.divider()
        page = st.radio(
            "Navigation",
            ["🔍 Search Videos", "🎬 Video List", "⬆️ Upload Video", "👤 User Profile"],
            label_visibility="collapsed",
        )
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    # ===================== PAGE: SEARCH =====================
    if page == "🔍 Search Videos":
        st.markdown("## 🔍 Search Video Content")
        st.markdown("Enter a description of the scene or content you want to search (in English or Vietnamese).")

        # Use a form to group inputs and avoid immediate reruns
        st.markdown("""
            <style>
                div[data-testid="stForm"] {
                    border: none;
                    padding: 0;
                }
            </style>
        """, unsafe_allow_html=True)
        with st.form("search_form"):
            col_input, col_topk, col_search = st.columns([3, 1, 1])
            with col_input:
                query = st.text_input(
                    "Search Query",
                    placeholder="e.g., a person walking on the street, crowd...",
                    value=st.session_state.search_query,                 
                )
            with col_topk:
                top_k = st.number_input(
                "Top K results",
                min_value=1,
                max_value=20,
                value=5,
                placeholder="Top K results",  
            )

            with col_search:
                st.markdown("<br>", unsafe_allow_html=True)
                search_submitted = st.form_submit_button("🔍 Search")

        if search_submitted:
            if not query.strip():
                st.warning("Please enter a search query.")
            else:
                with st.spinner("Searching..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/search/",
                            json={"query": query, "top_k": top_k},
                            timeout=60,
                        )
                        response.raise_for_status()
                        st.session_state.search_results = response.json()
                        st.session_state.search_query = query
                    except requests.exceptions.RequestException as e:
                        st.error(f"Search failed: {e}")
                        st.session_state.search_results = []
                        st.session_state.search_query = ""

        # Render stored search results (persists during video play reruns)
        if st.session_state.search_results is not None:
            results = st.session_state.search_results
            stored_query = st.session_state.search_query

            if not results:
                st.info("No matching results found. Try different keywords or upload more videos.")
            else:
                st.success(f"Found **{len(results)}** results for: *\"{stored_query}\"*")
                st.divider()

                # Video player area (appears when user clicks a Play button)
                if st.session_state.playing_video:
                    pv = st.session_state.playing_video
                    st.markdown(f"### ▶️ Now Playing: {pv['title']}")
                    st.caption(f"🕐 Starts at: {format_timestamp(pv['start_time'])}")
                    st.video(pv["url"], start_time=int(pv["start_time"]))
                    if st.button("✖ Close video"):
                        st.session_state.playing_video = None
                        st.rerun()
                    st.divider()

                # Display results in 2 columns
                cols = st.columns(2)
                for idx, result in enumerate(results):
                    with cols[idx % 2]:
                        ts = format_timestamp(result["timestamp_seconds"])
                        sim_pct = round(result["similarity"] * 100, 1)

                        # Frame thumbnail
                        if result.get("frame_url"):
                            try:
                                st.image(result["frame_url"], use_container_width=True)
                            except Exception:
                                st.markdown("🎞️ *Frame unavailable*")

                        # Card info
                        st.markdown(f"""
<div class="result-card">
    <div class="result-title">🎬 {result['title']}</div>
    <div class="result-meta">
        🕐 Timestamp: <strong>{ts}</strong> &nbsp;|&nbsp;
        <span class="similarity-badge">🎯 {sim_pct}%</span>
    </div>
</div>
""", unsafe_allow_html=True)

                        # Play button
                        if st.button(
                            f"▶ Play from {ts}",
                            key=f"play_{idx}_{result['video_id']}_{result['timestamp_seconds']}",
                            use_container_width=True,
                        ):
                            st.session_state.playing_video = {
                                "url": result["video_url"],
                                "start_time": result["timestamp_seconds"],
                                "title": result["title"],
                            }
                            st.rerun()

    # ===================== PAGE: VIEW VIDEOS =====================
    elif page == "🎬 Video List":
        st.markdown("## 🎬 Video List")

        col_refresh, _ = st.columns([1, 5])
        with col_refresh:
            if st.button("🔄 Refresh"):
                st.rerun()

        with st.spinner("Loading video list..."):
            try:
                response = requests.get(f"{BACKEND_URL}/videos/")
                response.raise_for_status()
                videos = response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Could not load videos. Make sure backend is running. Error: {e}")
                videos = []

        if not videos:
            st.info("No videos found. Upload your first video!")
        else:
            cols = st.columns(3)
            for i, video in enumerate(videos):
                with cols[i % 3]:
                    st.video(video["video_url"])
                    st.markdown(f"**{video['title']}**")

                    # Status badge
                    st.markdown(status_badge(video.get("status", "")), unsafe_allow_html=True)

                    try:
                        dt = datetime.fromisoformat(video["timestamp"])
                        st.caption(f"📅 {dt.strftime('%Y-%m-%d %H:%M')}")
                    except Exception:
                        st.caption(f"📅 {video.get('timestamp', '')}")
                    st.divider()

    # ===================== PAGE: UPLOAD =====================
    elif page == "⬆️ Upload Video":
        st.markdown("## ⬆️ Upload New Video")
        st.info(
            "After uploading, the AI pipeline automatically runs in the background: "
            "scene detection, frame extraction, and vector embedding creation for semantic search."
        )

        with st.form("upload_form"):
            title = st.text_input("Video title", max_chars=100)
            st.caption(f"Uploading as: **{user['email']}**")
            uploaded_file = st.file_uploader(
                "Select video file", type=["mp4", "mov", "avi", "mkv"]
            )
            submit_button = st.form_submit_button("⬆️ Upload Video", use_container_width=True)

            if submit_button:
                if not title:
                    st.warning("Please enter a video title.")
                elif not uploaded_file:
                    st.warning("Please select a video file.")
                else:
                    with st.spinner("Uploading video... Please wait."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            data = {"title": title, "user_id": user["user_id"]}
                            response = requests.post(
                                f"{BACKEND_URL}/videos/upload",
                                files=files,
                                data=data,
                                timeout=300,
                            )
                            response.raise_for_status()
                            st.success(
                                "✅ Upload successful! AI pipeline is running in the background to process the video. "
                                "It will be searchable in a few minutes."
                            )
                            st.json(response.json())
                        except requests.exceptions.RequestException as e:
                            st.error(f"Upload failed: {e}")
                            if hasattr(e, "response") and e.response is not None:
                                st.error(f"Server: {e.response.text}")

    # ===================== PAGE: USER PROFILE =====================
    elif page == "👤 User Profile":
        st.markdown("## 👤 User Profile")
        
        tab1, tab2, tab3 = st.tabs(["Profile Info", "Change Password", "My Videos"])
        
        with tab1:
            st.markdown("### Profile Information")
            st.markdown(f"**Email:** {user['email']}")
            
            with st.form("update_username_form"):
                new_username = st.text_input("Username", value=user['username'], max_chars=20)
                submit_username = st.form_submit_button("Update Username", use_container_width=True)
                if submit_username:
                    if not new_username or len(new_username) < 3:
                        st.warning("Username must be at least 3 characters.")
                    elif new_username == user['username']:
                        st.info("Username is the same.")
                    else:
                        with st.spinner("Updating username..."):
                            try:
                                response = requests.put(
                                    f"{BACKEND_URL}/user/username",
                                    json={"user_id": user["user_id"], "new_username": new_username}
                                )
                                response.raise_for_status()
                                st.session_state.user['username'] = new_username
                                st.success("Username updated successfully!")
                                st.rerun()
                            except requests.exceptions.RequestException as e:
                                st.error("Failed to update username.")
                                if hasattr(e, "response") and e.response is not None:
                                    st.error(f"Details: {e.response.text}")
        
        with tab2:
            st.markdown("### Change Password")
            with st.form("change_password_form"):
                old_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password (min 6 characters)", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                submit_password = st.form_submit_button("Change Password", use_container_width=True)
                
                if submit_password:
                    if not old_password or not new_password or not confirm_password:
                        st.warning("Please fill in all fields.")
                    elif new_password != confirm_password:
                        st.error("New passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("New password must be at least 6 characters.")
                    else:
                        with st.spinner("Changing password..."):
                            try:
                                response = requests.put(
                                    f"{BACKEND_URL}/user/password",
                                    json={"email": user["email"], "old_password": old_password, "new_password": new_password}
                                )
                                response.raise_for_status()
                                st.success("Password changed successfully!")
                            except requests.exceptions.RequestException as e:
                                st.error("Failed to change password. Please check your current password.")
                                if hasattr(e, "response") and e.response is not None:
                                    st.error(f"Details: {e.response.text}")
        
        with tab3:
            st.markdown("### My Uploaded Videos")
            col_refresh, _ = st.columns([1, 5])
            with col_refresh:
                if st.button("🔄 Refresh My Videos", key="refresh_my_videos"):
                    st.rerun()
                    
            with st.spinner("Loading your videos..."):
                try:
                    response = requests.get(f"{BACKEND_URL}/videos/user/{user['user_id']}")
                    response.raise_for_status()
                    my_videos = response.json()
                except requests.exceptions.RequestException as e:
                    st.error("Could not load your videos.")
                    my_videos = []
                    
            if not my_videos:
                st.info("You haven't uploaded any videos yet.")
            else:
                cols = st.columns(3)
                for i, video in enumerate(my_videos):
                    with cols[i % 3]:
                        st.video(video["video_url"])
                        st.markdown(f"**{video['title']}**")
                        st.markdown(status_badge(video.get("status", "")), unsafe_allow_html=True)
                        try:
                            dt = datetime.fromisoformat(video["timestamp"])
                            st.caption(f"📅 {dt.strftime('%Y-%m-%d %H:%M')}")
                        except Exception:
                            st.caption(f"📅 {video.get('timestamp', '')}")
                        st.divider()
