import streamlit as st

st.header("video uploader")

st.file_uploader("upload your video",accept_multiple_files=True,type="video")

show_uploaded_vid = st.toggle("show uploaded video")

if show_uploaded_vid:
    st.write("video: ")