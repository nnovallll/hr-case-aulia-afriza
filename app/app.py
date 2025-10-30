import streamlit as st
from supabase import create_client

# --- Connect Supabase client ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# --- Streamlit Sidebar Navigation ---
st.sidebar.title("📂 Menu Navigasi")
page = st.sidebar.radio(
    "Pilih Halaman:",
    ["Benchmark Form", "Benchmark Dashboard", "Talent Insights"]
)

st.title("🧠 Talent Match Intelligence")

st.markdown("""
Selamat datang di sistem Talent Match Intelligence.  
Gunakan menu di sidebar untuk:
1️⃣ Membuat dan menyimpan benchmark (Step 1)  
2️⃣ Melihat dashboard peran (Step 2)  
3️⃣ Menjelajahi insight AI (Step 3)
""")

# --- Routing sederhana ke masing-masing page ---
if page == "Benchmark Form":
    st.switch_page("pages/01_Benchmark_Form.py")
elif page == "Benchmark Dashboard":
    st.switch_page("pages/02_Benchmark_Dashboard.py")
elif page == "Talent Insights":
    st.switch_page("pages/03_Talent_Insights.py")
