import os, requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

def ai_reply(comment):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": f"You are REAL thrift shop in Eldoret. Reply to FB comment: '{comment}' in same language (EN/SW/Sheng), 1 short sentence, friendly. If price question say DM tuongee."}],
                "temperature": 0.7,
                "max_tokens": 60
            }, timeout=20)
        print(f"Groq raw: {r.text[:300]}")
        data = r.json()
        if 'choices' in data:
            return data['choices'][0]['message']['content'].strip()
        else:
            print(f"Groq error JSON: {data}")
            return "Asante sana! DM tuongee 🙏"
    except Exception as e:
        print(f"Groq exception: {e}")
        return "Poa sana! Karibu DM tuongee 🙏"

def run():
    try:
        posts = requests.get(f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/posts?access_token={FB_TOKEN}&limit=2").json()
        for post in posts.get('data', []):
            pid = post['id']
            comments = requests.get(f"https://graph.facebook.com/v20.0/{pid}/comments?access_token={FB_TOKEN}&filter=stream&fields=id,message,from").json()
            print(f"Comments: {comments}")
            for c in comments.get('data', []):
                if c.get('from', {}).get('id') == FB_PAGE_ID:
                    continue
                check = requests.get(f"https://graph.facebook.com/v20.0/{c['id']}/comments?access_token={FB_TOKEN}").json()
                if check.get('data'):
                    continue
                reply_text = ai_reply(c.get('message',''))
                if not reply_text:
                    reply_text = "Asante sana boss! DM tuongee 🙏"
                resp = requests.post(f"https://graph.facebook.com/v20.0/{c['id']}/comments",
                    data={"message": reply_text, "access_token": FB_TOKEN})
                print(f"FB Post Response: {resp.text} Status: {resp.status_code}")
    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    run()
