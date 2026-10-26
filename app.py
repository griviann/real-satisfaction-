import os, sys, requests, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAGE_TOKEN = os.getenv("PAGE_TOKEN") or os.getenv("FB_PAGE_TOKEN")
PAGE_ID = os.getenv("PAGE_ID") or os.getenv("FB_PAGE_ID")

if not GROQ_API_KEY:
    log.error("MISSING GROQ_API_KEY")
    sys.exit(1)

topic = "Biashara Ndogo"
lang = "SW"
prompt = f"Andika post fupi ya Facebook kuhusu {topic} Kisumu, kwa Kiswahili sanifu, watu wa biashara ndogo. Max 2 sentences."

log.info(f"SELECTED | topic={topic} | lang={lang}")

resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
    json={"model": "llama-3.1-8b-instant", "messages": [{"role":"user","content":prompt}], "max_tokens": 100},
    timeout=30)

data = resp.json()
log.info(f"GROQ_RAW_RESPONSE | {data}")

if "choices" not in data:
    log.error(f"GROQ_NO_CHOICES | {data}")
    sys.exit(1)

text = data["choices"][0]["message"]["content"].strip()
log.info(f"GROQ_OK | {text}")

# Facebook post
fb_resp = requests.post(f"https://graph.facebook.com/{PAGE_ID}/feed",
    data={"message": text, "access_token": PAGE_TOKEN})
log.info(f"FB_RESPONSE | {fb_resp.json()}")
if fb_resp.status_code == 200:
    log.info(f"POSTED | fb_id={fb_resp.json().get('id')}")
else:
    log.error(f"FB_FAIL | {fb_resp.text}")
    sys.exit(1)
