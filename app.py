import os, sys, random, logging, requests
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", stream=sys.stdout)
log = logging.getLogger("RealSatisfaction")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAGE_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN") or os.getenv("PAGE_TOKEN") or os.getenv("FB_PAGE_TOKEN")
PAGE_ID = os.getenv("FB_PAGE_ID") or os.getenv("PAGE_ID")

if not GROQ_API_KEY or not PAGE_TOKEN or not PAGE_ID:
    log.error("MISSING ENV")
    sys.exit(1)

PILLARS = [
    ("Biashara Ndogo Kenya", "Small business tips for Kenya", "EN"),
    ("Mazingira Kenya", "Mazingira safi na Kenya green", "SW"),
    ("Afya na Lishe", "Health and nutrition", "SW"),
    ("Elimu na Vijana", "Education and youth Kenya", "EN"),
    ("Utalii Kenya", "Tourism Maasai Mara, Diani", "EN"),
    ("Kilimo Kenya", "Modern farming Kenya", "SW"),
    ("Teknolojia Kenya", "Tech and online business Kenya", "EN"),
    ("Umoja wa Kenya", "Kenyan culture and unity", "SW"),
]

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # FIXED: free, working, non-reasoning
FACEBOOK_URL = f"https://graph.facebook.com/v23.0/{PAGE_ID}/feed"

def generate_post(topic, ctx, lang):
    if lang == "SW":
        prompt = f"Andika post fupi ya Facebook kuhusu {topic}. Muktadha: {ctx}. Tumia Kiswahili rahisi kwa Wakenya. Sentensi mbili max, herufi 280 max. Hashtag max 2. Rudisha ujumbe pekee."
    else:
        prompt = f"Write a short Facebook post about {topic}. Context: {ctx}. Simple English for Kenyans. Max 2 sentences, 280 chars. Max 2 hashtags. Return only post."

    r = requests.post(GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 150, "temperature": 0.7},
        timeout=30)
    
    # NEW: Show real Groq error if any
    log.info("GROQ_STATUS | %s", r.status_code)
    data = r.json()
    if "error" in data:
        log.error("GROQ_ERROR | %s", data)
        raise RuntimeError(f"Groq error: {data}")
    
    post = data["choices"][0]["message"]["content"].strip()
    if len(post) > 280: post = post[:277].rstrip() + "..."
    log.info("GROQ_OK | %s", post[:60])
    return post

def main():
    topic, ctx, lang = random.choice(PILLARS)
    log.info("START | bot=RealSatisfaction | lang=%s | topic=%s", lang, topic)
    post = generate_post(topic, ctx, lang)
    r = requests.post(FACEBOOK_URL, data={"message": post, "access_token": PAGE_TOKEN}, timeout=30)
    d = r.json()
    log.info("FB_RESP | %s", d)
    if not d.get("id"):
        log.error("FB_FAILED")
        sys.exit(1)
    log.info("POSTED | %s", d["id"])
    log.info("FINISHED")

if __name__ == "__main__": main()
