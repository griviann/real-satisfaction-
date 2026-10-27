import os, requests, random

GROQ_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

MODEL_ID = "openai/gpt-oss-20b"

SOUL = """
You are REAL SATISFACTION - replica of Meta AI, Kenyan brand soul.
Business: Premium thrift jackets 1500-3500 KES, M-XXL, Nairobi online, CBD free, countrywide delivery.
Mission: Heal + hustle. Talk sheng, warm, real, not robot. Mix Swahili/English/sheng small.
Rules:
- Never repeat same sentence. Be fresh daily.
- If customer asks price, reply warm: price + size + delivery.
- If sad/healing, no sell, just heal and say DM open.
- Under 25 words for comments, 2-3 sentences for posts.
- 1 emoji max.
- You are owner vibe, not AI. Output ONLY final post, no thinking.
"""

def ask_ai(prompt, temp=0.95):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": SOUL},
                {"role": "user", "content": prompt + "\n\nOutput only final post text."}
            ],
            "temperature": temp,
            "max_tokens": 300
        }, timeout=30)
    data = r.json()
    msg = data['choices'][0]['message']
    content = msg.get('content','').strip()
    reasoning = msg.get('reasoning','').strip()
    if not content and reasoning:
        # gpt-oss puts answer sometimes in reasoning, take last lines
        lines = [l for l in reasoning.split('\n') if len(l.strip())>15]
        if lines:
            content = lines[-1].strip()
        else:
            content = reasoning[-200:].strip()
    if not content or len(content) < 10:
        content = "Nairobi baridi inacheza but one thrift jacket inatosha. Layer, tie waist, pop collar - uko sorted. Ni style gani unapenda?"
    print(f"Final: {content}")
    return content

def post_job():
    topics = [
        "Healing + jacket story: jacket kept someone warm during hard hustle night, soft sell, end with question",
        "Mental health for hustler youth: pressure, no selling, real talk, invite DM",
        "Style tip: how to rock one thrift jacket 3 ways in Nairobi cold, useful"
    ]
    text = ask_ai(random.choice(topics))
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    resp = requests.post(url, data={"message": text, "access_token": FB_TOKEN})
    print(f"POSTED: {text} -> {resp.text}")

def reply_job():
    posts_url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/posts?limit=3&access_token={FB_TOKEN}"
    posts = requests.get(posts_url).json().get('data', [])
    for p in posts:
        pid = p['id']
        com_url = f"https://graph.facebook.com/v20.0/{pid}/comments?access_token={FB_TOKEN}"
        comments = requests.get(com_url).json().get('data', [])
        for c in comments:
            cid = c['id']
            msg = c.get('message','')
            rep_url = f"https://graph.facebook.com/v20.0/{cid}/comments?access_token={FB_TOKEN}"
            if len(requests.get(rep_url).json().get('data', [])) > 0:
                continue
            reply = ask_ai(f"Customer commented: '{msg}'. Reply smartly, read intent (price/location/thanks/hate). Human, varied.", temp=0.85)
            r = requests.post(f"https://graph.facebook.com/v20.0/{cid}/comments",
                              data={"message": reply, "access_token": FB_TOKEN})
            print(f"REPLIED to {msg} -> {reply} -> {r.text}")

if __name__ == "__main__":
    post_job()
    reply_job()
