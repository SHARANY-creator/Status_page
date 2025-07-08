from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATUSPAGE_API_KEY = os.getenv("STATUSPAGE_API_KEY")
PAGE_ID = "gssrvqwbzz91"
COMPONENT_MAP = {
    "jira": "vhrm0ww1rkwn",
    "agile": "6rvkdr8qyyr2",
    "confluence": "l9k0d6hn6t4l",
    "xray": "qr00w735vx7c"
}

@app.post("/dynatrace-webhook")
async def receive_dynatrace_webhook(request: Request):
    payload = await request.json()
    problem = payload.get("problem", {})

    title = problem.get("title", "")
    status = "partial_outage"  # default
    component_id = None

    # Determine component & status
    if "jira" in title.lower():
        component_id = COMPONENT_MAP["jira"]
    elif "confluence" in title.lower():
        component_id = COMPONENT_MAP["confluence"]
    elif "agile" in title.lower():
        component_id = COMPONENT_MAP["agile"]
    elif "xray" in title.lower():
        component_id = COMPONENT_MAP["xray"]

    if "closed" in title.lower():
        status = "operational"
    elif "duration" in title.lower() or "timeout" in title.lower():
        status = "degraded_performance"

    if not component_id:
        raise HTTPException(status_code=400, detail="Component not matched in title.")

    # Update component status on Statuspage
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{component_id}",
            headers={
                "Authorization": f"OAUTH {STATUSPAGE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"component": {"status": status}}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    return {"message": "Component status updated."}
