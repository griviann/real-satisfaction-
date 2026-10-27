import os, requests, random
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

TOPICS = [
    "social - loneliness, friendship, community",
    "psychological - stress, overthinking",
    "depression - hope, you are not alone",
    "economy pressure - hustle, budgeting",
    "unity - sisi wote ni Wakenya, peace"
]

def generate_post():
    topic = random.choice(TOPICS)
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are Kenyan mentor posting to heal society. No sales. Warm, short."},
                    {"role": "user", "content": f"Create 1 FB post about: {topic}. Kenyan youth, sheng mix, 2-3 sentences, 1 emoji, no hashtags. Day: {datetime.now().strftime('%A')}"}
                ],
                "temperature": 0.9,
                "max_tokens": 120
            }, timeout=20)
        return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return None

def post_to_fb(message):
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    resp = requests.post(url, data={"message": message, "access_token": FB_TOKEN})
    print(f"Posted: {message} -> {resp.text}")

if __name__ == "__main__":
    text = generate_post()
    if text:
        post_to_fb(text)
