from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

STATUSPAGE_API_KEY = os.getenv("STATUSPAGE_API_KEY")
PAGE_ID = os.getenv("STATUSPAGE_PAGE_ID")
COMPONENT_ID = os.getenv("STATUSPAGE_COMPONENT_ID")
STATUSPAGE_API_URL = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{COMPONENT_ID}.json"

class AlertData(BaseModel):
    problemTitle: str
    state: str

@app.post("/webhook")
async def receive_alert(alert: AlertData):
    if alert.state.lower() != "open":
        return {"message": "Alert ignored as state is not open"}

    headers = {
        "Authorization": f"OAUTH {STATUSPAGE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "component": {
            "status": "major_outage"
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(STATUSPAGE_API_URL, headers=headers, json=data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to update Statuspage")

    return {"message": "Statuspage updated successfully"}
