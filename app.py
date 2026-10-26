import os, sys, random, requests, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger()

# --- ENV (supports both names) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAGE_TOKEN = os.getenv("PAGE_TOKEN") or os.getenv("FB_PAGE_TOKEN")
PAGE_ID = os.getenv("PAGE_ID") or os.getenv("FB_PAGE_ID")

if not GROQ_API_KEY or not PAGE_TOKEN or not PAGE_ID:
    log.error(f"MISSING ENV | GROQ={'OK' if GROQ_API_KEY else 'MISSING'} PAGE_TOKEN={'OK' if PAGE_TOKEN else 'MISSING'} PAGE_ID={'OK' if PAGE_ID else 'MISSING'}")
    sys.exit(1)

# --- PILLARS - RealSatisfaction Kisumu ---
PILLARS = [
    ("Biashara Ndogo", "Tips za wafanyabiashara wadogo Kisumu, soko, wateja, pesa"),
    ("Mazingira Lake Victoria", "Usafi wa Ziwa Victoria, taka, mazingira Kisumu"),
    ("Afya na Lishe", "Afya ya jamii, lishe bora, hospitali Kisumu"),
    ("Elimu Vijana", "Elimu, ujuzi, ajira kwa vijana wa Kisumu"),
    ("Utalii Kisumu", "Maeneo ya kutembelea Kisumu, Dunga, Kit Mikayi, Impala"),
    ("Kilimo Kisumu", "Kilimo cha kisasa, samaki, mchele Ahero, biashara"),
]

topic, context = random.choice(PILLARS)
lang = "SW"
prompt = f"Andika post fupi ya Facebook (max 2 sentences, max 280 chars) kuhusu {topic} - {context}. Lugha: Kiswahili sanifu cha Kisumu, rahisi, chanya, chenye msaada. Usiweke hashtags nyingi, max 2. Usitaje wewe ni AI."

log.info(f"SELECTED | topic={topic} | lang={lang}")

# --- GROQ CALL (FIXED MODEL) ---
try:
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 120,
            "temperature": 0.8
        },
        timeout=30
    )
    data = resp.json()
    log.info(f"GROQ_RAW_RESPONSE | {data}")

    if "choices" not in data or not data["choices"]:
        log.error(f"GROQ_NO_CHOICES | {data}")
        sys.exit(1)

    text = data["choices"][0]["message"]["content"].strip()
    log.info(f"GROQ_OK | {text}")

except Exception as e:
    log.error(f"GROQ_FAIL
