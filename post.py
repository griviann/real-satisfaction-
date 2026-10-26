import os, requests, random
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

TOPICS = [
    "social - loneliness, friendship, community support",
    "psychological - stress, overthinking, mental health coping",
    "depression - hope, feeling low, small steps, you are not alone",
    "economy pressure - hustle, jobless youth, budgeting little money",
    "toning down political animosity - unity, peace, sisi wote ni Wakenya"
]

def generate_post():
    topic = random.choice(TOPICS)
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are Kenyan mentor posting to make society better. No sales. Healing, unity, hope."},
                    {"role": "user", "content": f"Create 1 Facebook post about: {topic}. Kenyan youth, sheng mix, warm, 2-3 sentences max, 1 emoji, no hashtags, never say AI. Date: {datetime.now().strftime('%A')}"}
                ],
                "temperature": 0.9,
                "max_tokens": 120
            }, timeout=20)
        return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return None

def post_to_fb(message):
    try:
        url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
        resp = requests.post(url, data={"message": message, "access_token": FB_TOKEN})
        print(f"Posted: {message} -> {resp.text}")
    except Exception as e:
        print(f"FB error: {e}")

if __name__ == "__main__":
    text = generate_post()
    if text:
        post_to_fb(text)
