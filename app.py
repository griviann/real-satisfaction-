import os, sys, random, logging, requests, re
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", stream=sys.stdout)
log = logging.getLogger("RealSatisfaction")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
PAGE_TOKEN=os.getenv("FB_PAGE_ACCESS_TOKEN") or os.getenv("PAGE_TOKEN")
PAGE_ID=os.getenv("FB_PAGE_ID")
PILLARS=[("Biashara Kenya","business","EN"),("Mazingira Kenya","mazingira","SW"),("Afya","health","SW"),("Elimu Kenya","education","EN"),("Utalii Kenya","tourism","EN"),("Kilimo Kenya","farming","SW")]
MODELS=["openai/gpt-oss-20b","qwen/qwen3-32b","llama-3.1-8b-instant"]
GROQ_URL="https://api.groq.com/openai/v1/chat/completions"
FB_URL=f"https://graph.facebook.com/v23.0/{PAGE_ID}/feed"
def clean(t): return re.sub(r'<think>.*?</think>','',t,flags=re.DOTALL).strip()
topic,ctx,lang=random.choice(PILLARS)
prompt=f"Write FB post about {topic} ({ctx}) in {lang}. 2 sentences max, 280 chars, 2 hashtags max. Return only post."
for m in MODELS:
 log.info("TRY %s",m)
 r=requests.post(GROQ_URL,headers={"Authorization":f"Bearer {GROQ_API_KEY}"},json={"model":m,"messages":[{"role":"user","content":prompt}],"max_tokens":200,"temperature":0.7},timeout=30)
 d=r.json()
 if "error" in d: log.warning("FAIL %s",d["error"]["message"][:120]); continue
 post=clean(d["choices"][0]["message"]["content"])[:280]
 log.info("OK %s %s",m,post[:60])
 rp=requests.post(FB_URL,data={"message":post,"access_token":PAGE_TOKEN},timeout=30)
 log.info("FB %s",rp.json())
 log.info("POSTED")
 sys.exit(0)
log.error("ALL FAILED"); sys.exit(1)
