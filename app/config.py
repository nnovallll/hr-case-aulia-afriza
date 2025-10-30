import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL"))
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

if not DATABASE_URL:
    st.error("❌ DATABASE_URL is not set. Please check your Streamlit Secrets or .env file.")
