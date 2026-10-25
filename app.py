import os
import json
from datetime import datetime

def log_autopsy(action, data, result):
    line = f"{datetime.now()} | {action} | {data} | {result}\n"
    with open("autopsy.log", "a") as f:
        f.write(line)
    print(line)

def ai_handler(action_type, data):
    text = str(data.get("text", "")).lower()
    category = data.get("category", "")
    bad_words = ["mjinga", "umbwa", "malaya", "shenzi", "fala"]
    for w in bad_words:
        if w in text:
            result = {"decision": "HIDE", "reason": f"matusi {w}"}
            log_autopsy(action_type, data, result)
            return result
    if "bunda" in text or "makalio" in text:
        if "afya" in text or category == "health":
            result = {"decision": "ALLOW", "reason": "bunda health allowed"}
            log_autopsy(action_type, data, result)
            return result
    if action_type == "post_draft":
        cat = data.get("category", "")
        if cat in ["politics", "health", "news"]:
            if not data.get("official_link"):
                result = {"decision": "REJECT", "reason": "needs official_link"}
                log_autopsy(action_type, data, result)
                return result
    result = {"decision": "ALLOW", "reason": "70pct joy 30pct trusted"}
    log_autopsy(action_type, data, result)
    return result

def generate_post(topic, category):
    official = "https://www.health.go.ke"
    if category == "politics":
        official = "https://www.iebc.or.ke"
    draft = {"text": f"Tunza afya {topic}", "category": category, "official_link": official}
    check = ai_handler("post_draft", draft)
    if check["decision"] == "ALLOW":
        return f"POSTED: {draft['text']}"
    else:
        return f"BLOCKED: {check['reason']}"
