import streamlit as st
import requests

@st.cache_resource
def get_ai_headers():
    provider = st.secrets["ai"]["provider"]
    api_key = st.secrets["ai"]["api_key"]
    if provider == "openrouter":
        return {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://openrouter.ai/",
            "X-Title": "Talent Match Intelligence"
        }
    return {"Authorization": f"Bearer {api_key}"}

def generate_ai_text(prompt, model=None):
    """Kirim prompt ke model AI (OpenRouter default)."""
    if model is None:
        model = st.secrets["ai"]["model"]
    headers = get_ai_headers()
    url = "https://openrouter.ai/api/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an HR data analyst assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Gagal generate AI response: {e}"
