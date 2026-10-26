import os, random, requests
from groq import Groq

def post_real():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Missing GROQ_API_KEY")
        return
    
    client = Groq(api_key=api_key)
    
    topics = [
        ("Afya mashinani", "https://www.health.go.ke", "Afya mashinani Kenya na matumaini"),
        ("Budget 2026", "https://www.treasury.go.ke", "Bajeti 2026 inagusa mwananchi wa kawaida"),
        ("IEBC na Amani", "https://www.iebc.or.ke", "IEBC na umuhimu wa amani ya taifa"),
        ("Kilimo biashara", "https://www.kilimo.go.ke", "Kilimo biashara kwa vijana wa Kenya"),
        ("Elimu bure", "https://www.education.go.ke", "Elimu bora kwa kila mtoto"),
        ("Utalii Kenya", "https://www.tourism.go.ke", "Utalii wa ndani unainua uchumi"),
        ("Maji safi", "https://www.water.go.ke", "Maji safi kwa kila boma"),
        ("Ajira vijana", "https://www.labour.go.ke", "Ajira na stadi kwa vijana"),
    ]
    
    theme, link, desc = random.choice(topics)
    
    prompt = f"Andika post fupi ya Real Satisfaction kuhusu {desc}, Kiswahili sanifu, 22 words max, hopeful, joy 70% trusted 30%, bila matusi"
    
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.choices[0].message.content.strip()
    
    # HIDE mjinga / punda filter
    if any(w in text.lower() for w in ["mjinga", "punda", "matako", "umbwa"]):
        print(f"HIDE filtered: {text}")
        return "HIDE"
    
    full = f"{text} {link} #RealSatisfaction #Kenya2026"
    
    token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    if token and page_id:
        url = f"https://graph.facebook.com/{page_id}/feed"
        r = requests.post(url, data={"message": full, "access_token": token, "link": link})
        print(f"POSTED [{theme}]: {full} -> {r.text}")
    else:
        print(f"DRY RUN [{theme}]: {full}")
    
    return full

if __name__ == "__main__":
    post_real()
