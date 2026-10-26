import os, requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

def ai_reply(comment):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [{"role": "user", "content": f"Reply to this Facebook comment as REAL page (Nairobi jackets + lifestyle). Same language as comment (EN/SW/Sheng), 1 sentence, friendly, if asking price say DM. Comment: {comment}"}],
                "temperature": 0.7,
                "max_tokens": 80
            }, timeout=30)
        return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Asante sana! DM tuongeze 🙏"

def run():
    try:
        posts = requests.get(f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/posts?access_token={FB_TOKEN}&limit=3").json()
        print(f"Posts found: {posts}")
        for post in posts.get('data', []):
            pid = post['id']
            comments = requests.get(f"https://graph.facebook.com/v20.0/{pid}/comments?access_token={FB_TOKEN}&filter=stream").json()
            print(f"Comments for {pid}: {comments}")
            for c in comments.get('data', []):
                # Skip if comment is from page itself
                if c.get('from', {}).get('id') == FB_PAGE_ID:
                    print(f"Skipped own comment {c['id']}")
                    continue
                replies = requests.get(f"https://graph.facebook.com/v20.0/{c['id']}/comments?access_token={FB_TOKEN}").json()
                if replies.get('data'):
                    print(f"Already replied to {c['id']}")
                    continue
                reply_text = ai_reply(c['message'])
                resp = requests.post(f"https://graph.facebook.com/v20.0/{c['id']}/comments",
                    data={"message": reply_text, "access_token": FB_TOKEN})
                print(f"Replied to {c['id']}: {reply_text}")
                print(f"FB API Response: {resp.text} Status: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__": 
    run()
