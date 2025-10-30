# 🧠 Talent Match Intelligence  
**Data Analyst Case Study 2025**

---

## 📌 Project Overview

**Talent Match Intelligence** is a data-driven HR analytics system designed to identify the success patterns of top-performing employees and measure how closely other employees match these patterns.  
The system integrates **SQL modeling**, **data analysis**, and **AI generation** to support leadership succession and internal mobility decisions using objective, data-driven insights.

---

## 🎯 Objectives

1. **Discover Success Patterns**  
   Analyze competency, psychometric, and behavioral data to identify factors that differentiate high performers (rating = 5).

2. **Operationalize Success Logic**  
   Build a **SQL-based engine** to calculate dynamic match rates between benchmark and candidate employees.

3. **Deploy AI-Powered Dashboard**  
   Develop a **Streamlit application** integrated with **Supabase** and **OpenRouter AI** for real-time analytics and AI-generated insights.

---

## 🧩 Repository Structure

```bash
hr-case-aulia-afriza/
│
├── app/
│   ├── app.py                     # Main Streamlit app entry point
│   ├── pages/
│   │   ├── 01_Benchmark_Form.py   # Page 1: Benchmark employee selection
│   │   ├── 02_Benchmark_Dashboard.py # Page 2: SQL results visualization
│   │   └── 03_Talent_Insights.py  # Page 3: AI-generated role insights
│   │
│   ├── components/
│   │   ├── db_utils.py            # Database connection and query executor
│   │   ├── visual_utils.py        # Plotly visualizations for dashboard
│   │
│   ├── queries/
│   │   └── step2_final_output.sql # Core SQL script for talent matching
│   │
│   ├── ai_generator.py            # OpenRouter AI text generation module
│   ├── requirements.txt           # Dependencies for Streamlit Cloud
│
├── README.md                      # Project documentation (this file)
└── .streamlit/
    └── secrets.toml               # (Private) DB credentials and API keys
