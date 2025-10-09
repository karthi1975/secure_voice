"""
Device Authentication Module

Manages authentication for edge devices (Raspberry Pi) with short-lived JWT tokens.

Security features:
- Device secrets never exposed to end users
- JWT tokens with 15-minute TTL
- Token refresh mechanism
- Device revocation support
"""

from typing import Dict, Any, Optional
import secrets
import time
import os
from datetime import datetime, timedelta
import jwt

# JWT secret for signing tokens
# IMPORTANT: Use fixed secret from environment or generate once and save
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
TOKEN_TTL_MINUTES = 15  # Short-lived tokens

# Device registry (in production, use database)
# Each device has: device_id, device_secret, customer_id, name, active
DEVICES = {
    "pi_urbanjungle_001": {
        "device_id": "pi_urbanjungle_001",
        "device_secret": "dev_secret_urbanjungle_abc123xyz",  # Strong secret
        "customer_id": "urbanjungle",
        "name": "Urban Jungle - Raspberry Pi #1",
        "active": True,
        "created_at": "2025-10-09T00:00:00Z"
    },
    # Add more devices here:
    # "pi_customer2_001": {
    #     "device_id": "pi_customer2_001",
    #     "device_secret": "dev_secret_customer2_def456uvw",
    #     "customer_id": "customer2",
    #     "name": "Customer 2 - Raspberry Pi #1",
    #     "active": True
    # },
}


def get_device(device_id: str) -> Optional[Dict[str, Any]]:
    """Get device configuration by device_id."""
    return DEVICES.get(device_id)


def validate_device_credentials(device_id: str, device_secret: str) -> Optional[Dict[str, Any]]:
    """
    Validate device credentials.

    Returns:
        Device config if valid, None otherwise
    """
    device = get_device(device_id)
    if not device:
        return None

    # Check if device is active
    if not device.get("active", False):
        return None

    # Validate secret
    if device["device_secret"] != device_secret:
        return None

    return device


def generate_device_token(device_id: str, customer_id: str) -> str:
    """
    Generate a short-lived JWT token for device.

    Token claims:
    - device_id: Device identifier
    - customer_id: Customer identifier
    - exp: Expiration time (15 minutes from now)
    - iat: Issued at time
    - type: "device_token"
    """
    now = datetime.utcnow()
    expiry = now + timedelta(minutes=TOKEN_TTL_MINUTES)

    payload = {
        "device_id": device_id,
        "customer_id": customer_id,
        "type": "device_token",
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp())
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_device_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode device JWT token.

    Returns:
        Token payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != "device_token":
            return None

        # Verify device still exists and is active
        device_id = payload.get("device_id")
        device = get_device(device_id)
        if not device or not device.get("active", False):
            return None

        return payload

    except jwt.ExpiredSignatureError:
        # Token expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None


def revoke_device(device_id: str) -> bool:
    """
    Revoke a device (set active=False).

    All existing tokens for this device will be rejected on next validation.
    """
    device = get_device(device_id)
    if not device:
        return False

    device["active"] = False
    DEVICES[device_id] = device
    return True


def get_device_info(device_id: str) -> Optional[Dict[str, Any]]:
    """
    Get public device info (without secret).
    """
    device = get_device(device_id)
    if not device:
        return None

    return {
        "device_id": device["device_id"],
        "customer_id": device["customer_id"],
        "name": device["name"],
        "active": device["active"],
        "created_at": device.get("created_at")
    }


def get_customer_id_from_device(device_id: str) -> Optional[str]:
    """
    Get customer_id associated with a device_id.

    Used for multi-tenant routing: device_id → customer_id → HA instance
    """
    device = get_device(device_id)
    if not device:
        return None

    return device.get("customer_id")


def generate_device_secret() -> str:
    """Generate a secure device secret."""
    return f"dev_secret_{secrets.token_urlsafe(32)}"


def register_new_device(device_id: str, customer_id: str, name: str) -> Dict[str, Any]:
    """
    Register a new device.

    Returns:
        Device config including generated secret
    """
    device_secret = generate_device_secret()

    device = {
        "device_id": device_id,
        "device_secret": device_secret,
        "customer_id": customer_id,
        "name": name,
        "active": True,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    DEVICES[device_id] = device
    return device
