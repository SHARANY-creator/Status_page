from fastapi import FastAPI, Request
import requests

app = FastAPI()

STATUSPAGE_API = "https://api.statuspage.io/v1/pages/gssrvqwbzz91/components"
API_KEY = "025a4fc78b9948daa4e2136df37f1257"
COMPONENT_IDS = {
    "vhrm0ww1rkwn": "Jira",
    "6rvkdr8qyyr2": "Agile Hive",
    "l9k0d6hn6t4l": "Confluence",
    "qr00w735vx7c": "Xray"
}

@app.post("/dynatrace-webhook")
async def dynatrace_webhook(request: Request):
    data = await request.json()
    component_id = data.get("component")
    status = data.get("status")

    if component_id not in COMPONENT_IDS:
        return {"error": "Invalid component ID"}

    url = f"{STATUSPAGE_API}/{component_id}.json"
    headers = {
        "Authorization": f"OAuth {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = { "component": { "status": status } }

    res = requests.patch(url, headers=headers, json=payload)
    return {"status": res.status_code, "response": res.text}
