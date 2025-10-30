import requests
from config import OPENROUTER_API_KEY

def generate_ai_job_profile(role_name, role_purpose):
    if not OPENROUTER_API_KEY:
        return "⚠️ AI generator unavailable: missing API key."

    prompt = f"""
    Generate a concise job profile for {role_name}.
    Purpose: {role_purpose}.
    Return in this format:

    **Job Requirements:**
    - ...

    **Key Responsibilities:**
    - ...

    **Personality Fit:**
    - ...
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Talent Match Intelligence",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
        "temperature": 0.7
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI request failed: {e}"
    

