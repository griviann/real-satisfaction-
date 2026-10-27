import os, requests, json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

def load_trained_dict():
    try:
        with open('dict.json','r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def detect_language(message):
    trained = load_trained_dict()
    if not trained:
        return "sheng"
    msg_lower = message.lower()
    hits = sum(1 for w in trained.keys() if w.lower() in msg_lower)
    return "maragoli" if hits >= 1 else "sheng"

def track_maragoli_speaker(user_id, user_name, message):
    if detect_language(message) != "maragoli":
        return False
    try:
        try:
            with open('followers_maragoli.json','r', encoding='utf-8') as f:
                followers = json.load(f)
        except:
            followers = {}
        followers[user_id] = {
            "name": user_name,
            "message": message,
            "count": followers.get(user_id, {}).get("count", 0) + 1
        }
        with open('followers_maragoli.json','w', encoding='utf-8') as f:
            json.dump(followers, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def get_user_name(user_id):
    try:
        r = requests.get(f"https://graph.facebook.com/{user_id}", params={"fields":"first_name","access_token":FB_TOKEN}, timeout=10)
        return r.json().get("first_name","there")
    except:
        return "there"

def ai_reply(message, name="there", msg_type="comment"):
    trained = load_trained_dict()
    sheng_context = ", ".join([f"{k}={v}" for k,v in list(trained.items())[-20:]])
    lang = detect_language(message)

    if lang == "maragoli":
        system_prompt = f"You are REAL SATISFACTION. User {name} spoke Maragoli. Reply in Maragoli mix using ONLY taught words: {sheng_context}. Do NOT invent Maragoli. Use name {name}. 1-2 sentences, 1 emoji."
    else:
        system_prompt = f"You are REAL SATISFACTION. User {name} spoke Sheng/Swahili. Reply in Sheng/Swahili, NOT Maragoli. Context: {sheng_context}. Use name {name}. 1-2 sentences, 1 emoji, varied."

    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model":"llama-3.1-8b-instant","messages":[{"role":"system","content":system_prompt},{"role":"user","content":message}],"temperature":0.9,"max_tokens":100}, timeout=20)
        return r.json()['choices'][0]['message']['content'].strip()
    except:
        return f"Poa {name}, DM tuongee 🙏"

def reply_to_inbox(sender_id, msg):
    name = get_user_name(sender_id)
    track_maragoli_speaker(sender_id, name, msg)
    reply = ai_reply(msg, name, "inbox")
    requests.post(f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/messages", params={"access_token":FB_TOKEN}, json={"recipient":{"id":sender_id},"message":{"text":reply}})
    return reply

def reply_to_comment(comment_id, msg, commenter_id=None):
    name = get_user_name(commenter_id) if commenter_id else "there"
    if commenter_id:
        track_maragoli_speaker(commenter_id, name, msg)
    reply = ai_reply(msg, name, "comment")
    requests.post(f"https://graph.facebook.com/v18.0/{comment_id}/comments", params={"access_token":FB_TOKEN}, json={"message":reply})
    return reply
