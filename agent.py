import os, requests, random

GROQ_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

MODEL_ID = "openai/gpt-oss-20b" # KEEP THIS - IT WORKS

SOUL = """
You are REAL SATISFACTION - Kenyan thrift brand soul. Premium jackets 1500-3500 KES, M-XXL, CBD free delivery.
Vibe: healing + hustle, sheng, warm, real owner, not AI.
You MUST think inside, then output ONLY final Facebook post (2-3 lines, 1 emoji max, ends with question).
"""

def ask_ai(prompt, temp=0.8):
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
            "reasoning_effort": "low"  # <-- LET IT REASON BUT FAST
        }, timeout=60)
    data = r.json()
    print(f"RAW: {data}")
    msg = data['choices'][0]['message']
    content = msg.get('content','').strip()
    reasoning = msg.get('reasoning','').strip()

    # If content empty, reasoning has final answer at end - extract it
    if not content and reasoning:
        # gpt-oss puts final answer after last \n\n
        parts = reasoning.strip().split('\n\n')
        content = parts[-1] if parts else reasoning[-300:]
        # clean thinking tags if any
        content = content.replace('**Final Answer:**','').replace('Final:','').strip()

    if not content or len(content) < 15:
        # still empty? use middle of reasoning not fallback coded
        content = reasoning[-250:].strip() if reasoning else "Leo baridi ya Nairobi? Jacket moja safi inabeba story yako. Uko tayari ku-rock?"

    print(f"Final Post: {content}")
    return content

def post_job():
    topics = [
        "Write healing + jacket story: jacket kept someone warm during hard hustle night in Nairobi, soft sell, end with question",
        "Write mental health post for hustler youth: pressure ya mtaa, no selling, real talk, invite DM",
        "Write style tip: how to rock one thrift jacket 3 ways in Nairobi cold, useful, question at end"
    ]
    text = ask_ai(random.choice(topics))
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/feed"
    resp = requests.post(url, data={"message": text, "access_token": FB_TOKEN})
    print(f"POSTED -> {resp.text}")

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
            reply = ask_ai(f"Customer commented: '{msg}'. Reply human, 20 words, sheng small, read intent.", temp=0.85)
            r = requests.post(f"https://graph.facebook.com/v20.0/{cid}/comments",
                              data={"message": reply, "access_token": FB_TOKEN})
            print(f"REPLIED -> {r.text}")

if __name__ == "__main__":
    post_job()
    reply_job()
