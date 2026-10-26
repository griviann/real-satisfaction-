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
                "messages": [
                    {
                        "role": "system",
                        "content": """You are REAL Kenyan youth mentor + thrift shop owner in Eldoret. Replica of friendly Meta AI.
Mission: Make Kenyan society better - social, psychological, depression support, economy pressure, tone down political animosity, unity. sisi wote ni Wakenya.
If shop question: reply warm + DM tuongee once. If sad/depressed: empathy, not alone, talk to trusted person. If politics hate: promote peace, no side-taking.
Rules: 1-2 sentences, 1 emoji, sheng mix, real human, never repeat tuongee twice, never say you are AI."""
                    },
                    {"role": "user", "content": f"Comment: '{comment}'"}
                ],
                "temperature": 0.8,
                "max_tokens": 100
            }, timeout=20)
        data = r.json()
        text = data['choices'][0]['message']['content'].strip() if 'choices' in data and data['choices'] else "Poa bro, DM tuongee 🙏"
        return text.replace("tuongee tuongee", "tuongee")
    except Exception as e:
        print(f"Groq error: {e}")
        return "Poa bro, DM tuongee 🙏"

def run():
    try:
        posts = requests.get(f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/posts?access_token={FB_TOKEN}&limit=3").json()
        for post in posts.get('data', []):
            pid = post['id']
            comments = requests.get(f"https://graph.facebook.com/v20.0/{pid}/comments?access_token={FB_TOKEN}&filter=stream&fields=id,message,from").json()
            for c in comments.get('data', []):
                if c.get('from', {}).get('id') == FB_PAGE_ID:
                    continue
                check = requests.get(f"https://graph.facebook.com/v20.0/{c['id']}/comments?access_token={FB_TOKEN}").json()
                if check.get('data'):
                    continue
                reply_text = ai_reply(c.get('message',''))
                requests.post(f"https://graph.facebook.com/v20.0/{c['id']}/comments",
                    data={"message": reply_text, "access_token": FB_TOKEN})
                print(f"Replied: {reply_text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
