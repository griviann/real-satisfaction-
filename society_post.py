import os, requests, random

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

FALLBACK = [
    "Monday reminder: You don't have to be perfect, just be present. Mtu mmoja at a time, step moja at a time. You got this 💙",
    "If today feels heavy, it's okay to rest. Kesho ni siku mpya. Talk to someone you trust 🤝",
    "Hustle ni real, but so is burnout. Pumzika kidogo, your mental health matters more than pressure 💚",
    "Kenyan youth, your story is not finished. Struggle ya leo ni strength ya kesho. Keep going 🌱"
]

def generate_post():
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are Kenyan mentor. Write 1 short healing FB post, 2-3 sentences, sheng mix, warm, no hashtags."},
                    {"role": "user", "content": "Write post about hope and resilience"}
                ],
                "temperature": 0.8,
                "max_tokens": 120
            }, timeout=25)
        data = r.json()
        print(f"Groq raw: {data}")
        if "choices" in data:
            return data['choices'][0]['message']['content'].strip()
        print("Using fallback")
        return random.choice(FALLBACK)
    except Exception as e:
        print(f"Error {e} fallback")
        return random.choice(FALLBACK)

def post_to_fb(message):
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    resp = requests.post(url, data={"message": message, "access_token": FB_TOKEN})
    print(f"Posted: {message} -> {resp.text}")

if __name__ == "__main__":
    text = generate_post()
    post_to_fb(text)
