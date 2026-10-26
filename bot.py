import os, requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

def ai_reply(comment):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": "openai/gpt-oss-20b",
            "messages": [{"role": "user", "content": f"Reply to this Facebook comment as REAL page (Nairobi jackets + lifestyle). Same language as comment (EN/SW/Sheng), 1 sentence, friendly, sell soft if asking price: 'DM'. Comment: {comment}"}],
            "temperature": 0.7,
            "max_tokens": 80
        })
    return r.json()['choices'][0]['message']['content'].strip()

def run():
    # get recent posts
    posts = requests.get(f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/posts?access_token={FB_TOKEN}&limit=5").json()
    for post in posts.get('data', []):
        pid = post['id']
        comments = requests.get(f"https://graph.facebook.com/v20.0/{pid}/comments?access_token={FB_TOKEN}&filter=stream").json()
        for c in comments.get('data', []):
            # check if we already replied
            replies = requests.get(f"https://graph.facebook.com/v20.0/{c['id']}/comments?access_token={FB_TOKEN}").json()
            if replies.get('data'): continue
            reply_text = ai_reply(c['message'])
            requests.post(f"https://graph.facebook.com/v20.0/{c['id']}/comments",
                data={"message": reply_text, "access_token": FB_TOKEN})
            print(f"Replied to {c['id']}: {reply_text}")

if __name__ == "__main__": run()
