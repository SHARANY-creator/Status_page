from fastapi import FastAPI, Request
import os, requests

app = FastAPI()

STATUSPAGE_API_KEY = os.getenv("STATUSPAGE_API_KEY")
PAGE_ID = "gssrvqwbzz91"
COMPONENT_MAP = {
    "jira": "vhrm0ww1rkwn",
    "confluence": "l9k0d6hn6t4l",
    "agile": "6rvkdr8qyyr2",
    "xray": "qr00w735vx7c"
}

@app.post("/")
async def update_status(request: Request):
    data = await request.json()
    text = data.get("text", "").lower()

    # Match component
    component_id = None
    for key, value in COMPONENT_MAP.items():
        if key in text:
            component_id = value
            break

    if not component_id:
        return {"error": "Component not matched"}

    # Match status
    if "connection timeout" in text:
        status = "partial_outage"
    elif "duration" in text or "above normal" in text:
        status = "degraded_performance"
    elif "closed" in text:
        status = "operational"
    else:
        return {"error": "Status not matched"}

    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{component_id}.json"
    headers = {
        "Authorization": f"OAuth {STATUSPAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"component": {"status": status}}

    r = requests.patch(url, json=payload, headers=headers)
    return {"status": r.status_code, "response": r.json()}
