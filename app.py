import os
import sys
import random
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("RealSatisfaction")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAGE_TOKEN = (
    os.getenv("FB_PAGE_ACCESS_TOKEN")
    or os.getenv("PAGE_TOKEN")
    or os.getenv("FB_PAGE_TOKEN")
)
PAGE_ID = os.getenv("FB_PAGE_ID") or os.getenv("PAGE_ID")

if not GROQ_API_KEY or not PAGE_TOKEN or not PAGE_ID:
    log.error(
        "MISSING ENV | GROQ=%s | PAGE_TOKEN=%s | PAGE_ID=%s",
        "OK" if GROQ_API_KEY else "MISSING",
        "OK" if PAGE_TOKEN else "MISSING",
        "OK" if PAGE_ID else "MISSING",
    )
    sys.exit(1)

PILLARS = [
    ("Biashara Ndogo","Vidokezo vya biashara ndogo, wateja, masoko na usimamizi wa pesa Kisumu."),
    ("Mazingira na Ziwa Victoria","Usafi wa Ziwa Victoria, utunzaji wa taka na mazingira safi Kisumu."),
    ("Afya na Lishe","Afya ya jamii, lishe bora na elimu ya afya."),
    ("Elimu na Vijana","Elimu, ujuzi, kujifunza na fursa za vijana Kisumu."),
    ("Utalii Kisumu","Utalii wa Kisumu, Dunga, Kit Mikayi na Kisumu Impala Sanctuary."),
    ("Kilimo Kisumu","Kilimo cha kisasa, ufugaji wa samaki, mpunga wa Ahero na biashara ya mazao."),
]

BLOCKED_WORDS = ("mjinga","punda","matako","umbwa",)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"
API_VERSION = os.getenv("FACEBOOK_API_VERSION", "v23.0")
FACEBOOK_URL = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/feed"

def generate_post(topic, context):
    prompt = (
        f"Andika post fupi ya Facebook kuhusu {topic}. Muktadha: {context}. "
        "Tumia Kiswahili rahisi, sanifu na kinachoeleweka kwa watu wa Kisumu. "
        "Ujumbe uwe chanya, wenye heshima na manufaa kwa jamii. Usizidi sentensi mbili au herufi 280. "
        "Tumia hashtag zisizozidi mbili. Usibuni takwimu, habari au madai yasiyothibitishwa. Usitaje kuwa wewe ni AI. Rudisha ujumbe pekee."
    )
    try:
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}","Content-Type": "application/json"},
            json={"model": GROQ_MODEL,"messages": [{"role": "user","content": prompt}],"max_tokens": 120,"temperature": 0.7},
            timeout=30,
        )
        if not response.ok:
            log.error("ERROR | stage=groq | status=%s | response=%s", response.status_code, response.text[:300])
            raise RuntimeError("Groq API request failed")
        data = response.json()
    except requests.RequestException as exc:
        log.error("ERROR | stage=groq_network | type=%s", type(exc).__name__)
        raise
    except ValueError:
        log.error("ERROR | stage=groq_json")
        raise

    choices = data.get("choices", [])
    if not choices:
        log.error("ERROR | stage=groq_response | detail=%s", str(data.get("error", {}))[:250])
        raise RuntimeError("Groq returned no choices")

    msg = choices[0].get("message", {}) or {}
    post = (msg.get("content") or msg.get("reasoning_content") or "").strip()

    if not post:
        log.error("ERROR | stage=groq_response | empty_post | raw=%s", str(msg)[:400])
        raise RuntimeError("Groq returned empty text")

    if len(post) > 280:
        post = post[:277].rstrip() + "..."
    log.info("GROQ_OK | characters=%s", len(post))
    return post

def moderate_post(post, topic):
    lowered = post.casefold()
    for word in BLOCKED_WORDS:
        if word.casefold() in lowered:
            log.warning("HIDE | reason=blocked_word | topic=%s", topic)
            return False
    return True

def publish_post(post, topic):
    if not moderate_post(post, topic):
        return
    try:
        response = requests.post(FACEBOOK_URL,data={"message": post,"access_token": PAGE_TOKEN},timeout=30)
        try:
            data = response.json()
        except ValueError:
            log.error("ERROR | stage=facebook_json | status=%s", response.status_code)
            raise RuntimeError("Facebook returned invalid JSON")
        if not response.ok or not data.get("id"):
            error = data.get("error", {})
            if isinstance(error, dict):
                code = error.get("code", "unknown")
                message = str(error.get("message", "Unknown error"))[:250]
            else:
                code = "unknown"
                message = "Unknown Facebook error"
            log.error("ERROR | stage=facebook | status=%s | code=%s | message=%s", response.status_code, code, message)
            raise RuntimeError("Facebook publishing failed")
        log.info("POSTED | topic=%s | id=%s", topic, data["id"])
    except requests.RequestException as exc:
        log.error("ERROR | stage=facebook_network | type=%s", type(exc).__name__)
        raise

def main():
    topic, context = random.choice(PILLARS)
    log.info("START | bot=RealSatisfaction | lang=SW")
    log.info("SELECTED | topic=%s", topic)
    post = generate_post(topic, context)
    log.info("MODERATION_CHECK | topic=%s", topic)
    publish_post(post, topic)
    log.info("FINISHED | topic=%s", topic)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.error("ERROR | type=%s | message=%s", type(exc).__name__, str(exc))
        sys.exit(1)
