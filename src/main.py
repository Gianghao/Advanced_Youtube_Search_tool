import streamlit as st
import sys
from pathlib import Path

root_path = str(Path(__file__).parent)
if root_path not in sys.path:
    sys.path.append(root_path)

st.set_page_config(
    page_title="Login",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed",   
    menu_items={}                        
)

st.switch_page("pages/login_page.py")