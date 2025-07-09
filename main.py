from fastapi import FastAPI, Request, HTTPException
import requests
import os

app = FastAPI()

# Your Statuspage page ID and API key (use environment variables in Render)
STATUSPAGE_API_KEY = os.getenv("STATUSPAGE_API_KEY", "<your_api_key>")
STATUSPAGE_PAGE_ID = os.getenv("STATUSPAGE_PAGE_ID", "gssrvqwbzz91")

# Component mappings
COMPONENT_IDS = {
    "jira": "vhrm0ww1rkwn",
    "agile": "6rvkdr8qyyr2",
    "conflu": "l9k0d6hn6t4l",
    "xray": "qr00w735vx7c"
}

# Dynatrace/Zapier → FastAPI → Statuspage
@app.post("/dynatrace-webhook")
async def handle_dynatrace_webhook(request: Request):
    try:
        data = await request.json()
        title = data.get("problem_title", "").lower()
        body = data.get("body", "").lower()

        component_id = ""
        status = ""

        # Determine component
        for keyword, comp_id in COMPONENT_IDS.items():
            if keyword in title or keyword in body:
                component_id = comp_id
                break

        if not component_id:
            return {"error": "Component not matched in title or body."}

        # Determine status
        if "closed" in title:
            status = "operational"
        elif "duration" in title or "timeout" in title or "value was above" in body:
            status = "degraded_performance"
        else:
            status = "partial_outage"

        # Update Statuspage
        url = f"https://api.statuspage.io/v1/pages/{STATUSPAGE_PAGE_ID}/components/{component_id}.json"
        headers = {
            "Authorization": f"OAuth {STATUSPAGE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"component": {"status": status}}

        response = requests.patch(url, headers=headers, json=payload)

        if response.status_code == 200:
            return {"message": f"Component updated to '{status}'", "component_id": component_id}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
