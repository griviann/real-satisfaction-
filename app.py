import os, random, logging, sys, requests

# === REAL SATISFACTION LOGGING ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", handlers=[logging.StreamHandler(sys.stdout)], force=True)
log = logging.getLogger("RealSatisfaction")

# === YOUR 7 PILLARS COVERAGE + LINKS ===
TOPICS = {
    "Afya mashinani": "https://realsatisfaction.co.ke/afya",
    "Kilimo na Chakula": "https://realsatisfaction.co.ke/kilimo",
    "Budget 2026 na Uchumi": "https://realsatisfaction.co.ke/budget2026",
    "IEBC na Uongozi": "https://realsatisfaction.co.ke/iebc",
    "Elimu na Vijana": "https://realsatisfaction.co.ke/elimu",
    "Mazingira Lake Victoria": "https://realsatisfaction.co.ke/mazingira",
    "Biashara Ndogo": "https://realsatisfaction.co.ke/biashara"
}

# MOST INTEREST - weighted 2x
PRIORITY = ["Afya mashinani", "Kilimo na Chakula", "Budget 2026 na Uchumi"]
weighted_list = list(TOPICS.keys()) + PRIORITY
ENGLISH_TOPICS = {"Budget 2026 na Uchumi", "IEBC na Uongozi"}

topic = random.choice(weighted_list)
link = TOPICS[topic]
is_english = topic in ENGLISH_TOPICS
log.info(f"SELECTED | topic={topic} | lang={'EN' if is_english else 'SW'}")

# === SECRETS ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAGE_TOKEN = os.getenv("PAGE_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

# === PROMPT WITH JUDGEMENT ===
if is_english:
    prompt = f"Write hopeful factual Facebook post max 22 words about {topic} Kenya. No insults, hopeful. End with {link} #RealSatisfaction"
else:
    prompt = f"Andika post ya Kiswahili matumaini maneno 22 max kuhusu {topic}. Tumaini ukweli bila matusi. Mwisho weka {link} #RealSatisfaction"

# === GROQ CALL ===
try:
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "max_tokens": 80},
        timeout=30)
    text = r.json()["choices"][0]["message"]["content"].strip()
    log.info(f"GROQ_OK | {text}")
except Exception as e:
    log.error(f"GROQ_FAIL | {e}")
    sys.exit(1)

# === FILTER - BANNED WORDS ===
BANNED = ["mjinga", "punda", "umbwa"]
if any(w in text.lower() for w in BANNED):
    log.warning(f"FILTERED | banned word in: {text}")
    sys.exit(0)

# === POST TO FACEBOOK ===
try:
    fb = requests.post(f"https://graph.facebook.com/{PAGE_ID}/feed",
        data={"message": text, "access_token": PAGE_TOKEN}, timeout=30)
    log.info(f"POSTED | fb_id={fb.json().get('id')} | {text}")
except Exception as e:
    log.error(f"FB_FAIL | {e}")
    sys.exit(1)
