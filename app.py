import os
from groq import Groq
import google.generativeai as genai

# Setup both
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_ai_reply(user_text):
    # 1. Try GROQ Llama first (free, fast)
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_text}],
            temperature=0.7,
            max_tokens=1024
        )
        msg = resp.choices[0].message
        content = getattr(msg, 'content', None) or ""
        reasoning = getattr(msg, 'reasoning_content', None) or ""
        final = content.strip() or reasoning.strip()
        if final:
            return final
    except Exception as e:
        print(f"Groq failed: {e}")

    # 2. Fallback to Gemini if Groq fails
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(user_text)
        # This handles all Gemini formats
        if hasattr(resp, 'text') and resp.text:
            return resp.text.strip()
        if resp.candidates:
            return resp.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        print(f"Gemini failed: {e}")

    return "Sorry, try again"

# Use it
bot_text = get_ai_reply(user_message)
