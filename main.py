from fastapi import FastAPI, Request, HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

STATUSPAGE_API_KEY = os.getenv("STATUSPAGE_API_KEY")
PAGE_ID = "gssrvqwbzz91"
COMPONENT_ID = "vhrm0ww1rkwn"

STATUSPAGE_API_URL = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{COMPONENT_ID}"
HEADERS = {
    "Authorization": f"OAUTH {STATUSPAGE_API_KEY}",
    "Content-Type": "application/json"
}

@app.post("/dynatrace-alert")
async def handle_dynatrace_alert(request: Request):
    payload = await request.json()

    try:
        title = payload.get("title", "Dynatrace Alert")
        problem_impact = payload.get("impactLevel", "").lower()
        state = payload.get("state", "OPEN")

        print("🔔 Received alert:", title)

        # Simple rule: if alert is OPEN and impact is high, mark component as 'major_outage'
        if state == "OPEN" and "high" in problem_impact:
            status = "major_outage"
        elif state == "RESOLVED":
            status = "operational"
        else:
            status = "degraded_performance"

        async with httpx.AsyncClient() as client:
            res = await client.patch(
                STATUSPAGE_API_URL,
                headers=HEADERS,
                json={"component": {"status": status}}
            )
            if res.status_code not in (200, 202):
                raise HTTPException(status_code=500, detail="Failed to update component")

        return {"message": f"Component status set to {status}"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
