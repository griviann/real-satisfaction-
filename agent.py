import os, requests, random

GROQ_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

MODEL_ID = "openai/gpt-oss-20b"

SOUL = """
You are REAL SATISFACTION - owner of Kenyan thrift brand. Jackets 1500-3500 KES, M-XXL, CBD free delivery, countrywide.
Voice: sheng, Swahili, English mix, warm, real, hustler healer, not AI robot.
You MUST internally reason, then output ONLY 1 final Facebook post. 2-3 sentences max, 1 emoji max, end with question. Never repeat old posts.
"""

def ask_ai(prompt, temp=0.85):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": SOUL},
                {"role": "user", "content": prompt}
            ],
            "temperature": temp,
            "max_tokens": 1024,
            "reasoning_effort": "low"
        }, timeout=60)
    data = r.json()
    print(f"RAW: {data}")
    msg = data['choices'][0]['message']
    content = msg.get('content','').strip()
    reasoning = msg.get('reasoning','').strip()

    if not content and reasoning:
        parts = [p.strip() for p in reasoning.split('\n\n') if len(p.strip()) > 20]
        content = parts[-1] if parts else reasoning[-400:].strip()
        content = content.replace('**Final Answer:**','').replace('Final Post:','').strip()

    if not content or len(content) < 15:
        content = reasoning[-350:].strip() if reasoning else "Hustle ni hard but uko si alone. DM tuongee?"

    print(f"FINAL: {content}")
    return content

def post_job():
    # open topic - never coded, AI decides
    prompts = [
        "Create a healing post for hustlers feeling pressure ya mtaa, no selling, invite DM, end with question",
        "Create a jacket story: how one thrift jacket warmed someone during Nairobi cold hustle night, soft sell 1500-3500, end with question",
        "Create style tip: rock one thrift jacket 3 ways in Nairobi, useful, end with question",
        "Create real talk: dreams vs doubts for Nairobi youth, healing before hustle, end with question"
    ]
    text = ask_ai(random.choice(prompts))
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    resp = requests.post(url, data={"message": text, "access_token": FB_TOKEN})
    print(f"POST RESPONSE: {resp.text}")

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
            rep_check = f"https://graph.facebook.com/v20.0/{cid}/comments?access_token={FB_TOKEN}"
            if len(requests.get(rep_check).json().get('data', [])) > 0:
                continue
            reply = ask_ai(f"Customer commented: '{msg}'. Reply 20 words max, human, sheng small, understand intent (price/location/thanks).", temp=0.85)
            r = requests.post(f"https://graph.facebook.com/v20.0/{cid}/comments",
                              data={"message": reply, "access_token": FB_TOKEN})
            print(f"REPLY RESPONSE: {r.text}")

if __name__ == "__main__":
    post_job()
    reply_job()
