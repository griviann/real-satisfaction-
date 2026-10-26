# Ndani ya app.py - function moja inamaliza monotony
def post_real():
    import os, random, requests
    from groq import Groq
    
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    topics = [
        ("Afya", "https://health.go.ke"),
        ("Budget", "https://treasury.go.ke"),
        ("IEBC", "https://iebc.or.ke"),
        ("Kilimo", "https://kilimo.go.ke")
    ]
    theme, link = random.choice(topics)
    
    prompt = f"Andika post ya Real Satisfaction kuhusu {theme} Kenya, 20 words max, Kiswahili, tone hopeful"
    text = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
    
    # HIDE mjinga filter
    if any(w in text.lower() for w in ["mjinga", "punda"]):
        return "HIDE"
    
    # Post direct bila Codemagic
    token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    r = requests.post(f"https://graph.facebook.com/{page_id}/feed",
                      data={"message": f"{text} {link}", "access_token": token})
    print(r.text)
    return text
