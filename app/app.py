import streamlit as st
from components.db_utils import get_engine

st.set_page_config(
    page_title="Talent Match Intelligence",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Talent Match Intelligence")
st.markdown("""
Selamat datang di sistem Talent Match Intelligence.  
Gunakan menu di sidebar untuk:
1️⃣ Membuat dan menyimpan benchmark (Step 1)  
2️⃣ Melihat dashboard peran (Step 2)  
3️⃣ Menjelajahi insight AI (Step 3)
""")

# Tes koneksi DB
engine = get_engine()
with engine.connect() as conn:
    st.success("✅ Database connected successfully.")
