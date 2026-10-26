import os, sys, random, logging, requests, re
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", stream=sys.stdout)
log = logging.getLogger("RealSatisfaction")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
PAGE_TOKEN=os.getenv("FB_PAGE_ACCESS_TOKEN") or os.getenv("PAGE_TOKEN")
PAGE_ID=os.getenv("FB_PAGE_ID")
PILLARS=[("Biashara Kenya","business","EN"),("Mazingira Kenya","mazingira","SW"),("Afya","health","SW"),("Elimu Kenya","education","EN"),("Utalii Kenya","tourism","EN"),("Kilimo Kenya","farming","SW")]
# FIXED: Use real Groq models only
MODELS=["llama-3.1-8b-instant","llama-3.3-70b-versatile","openai/gpt-oss-20b"]
GROQ_URL="https://api.groq.com/openai/v1/chat/completions"
FB_URL=f"https://graph.facebook.com/v23.0/{PAGE_ID}/feed"

def clean(t):
    if not t: return ""
    t = re.sub(r'<think>.*?</think>','',t,flags=re.DOTALL).strip()
    t = t.strip().strip('"').strip("'").strip()
    return t

topic,ctx,lang=random.choice(PILLARS)
prompt=f"Write FB post about {topic} ({ctx}) in {lang}. 2 sentences max, 280 chars, 2 hashtags max. Return only post."

for m in MODELS:
    log.info("TRY %s",m)
    try:
        r=requests.post(GROQ_URL,headers={"Authorization":f"Bearer {GROQ_API_KEY}"},json={"model":m,"messages":[{"role":"user","content":prompt}],"max_tokens":200,"temperature":0.7},timeout=30)
        d=r.json()
        if "error" in d: 
            log.warning("FAIL %s %s",m, d["error"]["message"][:200])
            continue
        raw = d["choices"][0]["message"]["content"]
        post=clean(raw)[:280]
        if not post or len(post) < 10:
            log.warning("EMPTY from %s raw=%s", m, str(raw)[:200])
            continue
        log.info("OK %s %s",m,post[:80])
        rp=requests.post(FB_URL,data={"message":post,"access_token":PAGE_TOKEN},timeout=30)
        fb_data = rp.json()
        log.info("FB %s",fb_data)
        if "error" not in fb_data:
            log.info("POSTED %s", post)
            sys.exit(0)
        else:
            log.warning("FB failed, trying next model")
            continue
    except Exception as e:
        log.warning("EXCEPTION %s %s", m, e)
        continue

# Final fallback if all AI fails — so it ALWAYS posts
fallback = f"{topic}: Jenga biashara yako na bidii na maarifa. Mafanikio ni safari! #REALsatisfaction #Kenya"
log.info("USING FALLBACK %s", fallback)
rp=requests.post(FB_URL,data={"message":fallback,"access_token":PAGE_TOKEN},timeout=30)
log.info("FB FALLBACK %s",rp.json())
sys.exit(0)
