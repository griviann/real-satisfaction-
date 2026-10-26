import os, sys, random, logging, requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", stream=sys.stdout)
log = logging.getLogger("RealSatisfaction")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAGE_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN") or os.getenv("PAGE_TOKEN") or os.getenv("FB_PAGE_TOKEN")
PAGE_ID = os.getenv("FB_PAGE_ID") or os.getenv("PAGE_ID")

if not GROQ_API_KEY or not PAGE_TOKEN or not PAGE_ID:
    log.error("MISSING ENV")
    sys.exit(1)

# ORIGINAL OBJECTIVE RESTORED: Both English & Kiswahili depending on pillar
PILLARS = [
    ("Biashara Ndogo Kenya", "Small business tips for Kenya", "EN"),
    ("Mazingira Kenya", "Mazingira safi na Kenya green", "SW"),
    ("Afya na Lishe", "Health and nutrition for families", "SW"),
    ("Elimu na Vijana", "Education and youth opportunities in Kenya", "EN"),
    ("Utalii Kenya", "Tourism - Maasai Mara, Diani, Mt Kenya", "EN"),
    ("Kilimo Kenya", "Modern farming and fish farming Kenya", "SW"),
    ("Teknolojia Kenya", "Tech, online business in Kenya", "EN"),
    ("Umoja wa Kenya", "Kenyan culture, unity and heritage", "SW"),
]

BLOCKED_WORDS = ("mjinga","punda","matako","umbwa")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
FACEBOOK_URL = f"https://graph.facebook.com/v23.0/{PAGE_ID}/feed"

def generate_post(topic, context, lang):
    if lang == "SW":
        prompt = f"Andika post fupi ya Facebook kuhusu {topic}. Muktadha: {context}. Tumia Kiswahili rahisi, sanifu kwa Wakenya. Sentensi mbili max, herufi 280 max. Hashtag max 2. Rudisha ujumbe pekee."
    else:
        prompt = f"Write a short Facebook post about {topic}. Context: {context}. Use simple, clear English for Kenyans. Max 2 sentences, 280 chars. Max 2 hashtags. Return only the post."

    r = requests.post(GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 150, "temperature": 0.7},
        timeout=30)
    
    data = r.json()
    post = data["choices"][0]["message"]["content"].strip()
    if len(post) > 280:
        post = post[:277].rstrip() + "..."
    log.info("GROQ_OK | lang=%s | %s", lang, post[:60])
    return post

def main():
    topic, ctx, lang = random.choice(PILLARS)
    log.info("START | bot=RealSatisfaction | lang=%s | topic=%s", lang, topic)
    post = generate_post(topic, ctx, lang)
    
    # moderation
    if any(w in post.casefold() for w in BLOCKED_WORDS):
        log.warning("BLOCKED")
        return
    
    r = requests.post(FACEBOOK_URL, data={"message": post, "access_token": PAGE_TOKEN}, timeout=30)
    d = r.json()
    if not d.get("id"):
        log.error("FB_ERROR | %s", d)
        sys.exit(1)
    log.info("POSTED | id=%s", d["id"])
    log.info("FINISHED")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("ERROR | %s", e)
        sys.exit(1)
