#!/usr/bin/env python3
"""
VAPI Webhook Authentication Server
Validates customer_id and password server-side
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()


class VapiMessage(BaseModel):
    """VAPI message structure"""
    type: str
    content: Optional[str] = None


class VapiWebhookRequest(BaseModel):
    """VAPI webhook request"""
    message: VapiMessage
    call: Optional[dict] = None


@app.post("/vapi/auth")
async def authenticate(request: VapiWebhookRequest):
    """
    Authenticate based on message content.

    Expected format: "customer_id:password rest of message"
    Valid credentials: "urbanjungle:alpha-bravo-123"
    """

    message_content = request.message.content or ""

    # Extract credentials from message
    if ":" in message_content:
        parts = message_content.split(" ", 1)
        credentials = parts[0]

        # Check if credentials match
        if credentials == "urbanjungle:alpha-bravo-123":
            # Authentication successful
            greeting = parts[1] if len(parts) > 1 else "How can I help you?"

            return {
                "message": {
                    "type": "assistant",
                    "content": f"Welcome! Authentication successful. I'm Luna, your smart home assistant. {greeting}"
                }
            }

    # Authentication failed
    return {
        "message": {
            "type": "assistant",
            "content": "Authentication failed"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("🔐 VAPI Authentication Webhook Server")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:8001")
    print("Webhook endpoint: http://0.0.0.0:8001/vapi/auth")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8001)
