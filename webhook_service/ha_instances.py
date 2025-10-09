"""
Home Assistant Instance Configuration

Simplified Authentication - No Passwords Required!
- customer_id: Unique identifier (authenticated via VAPI Bearer token)
- ha_url: Home Assistant instance URL
- ha_webhook_id: Webhook ID for this instance
- name: Friendly name for the location

Authentication Flow:
1. VAPI sends Bearer token + x-customer-id header
2. Webhook validates Bearer token = proves request is from VAPI
3. customer_id → maps to correct HA instance
4. Commands routed to customer's HA instance
"""

from typing import Dict, Any, Optional

# Home Assistant instances configuration
# In production, load from environment variables or database
HA_INSTANCES = {
    "urbanjungle": {
        "customer_id": "urbanjungle",
        "ha_url": "https://ut-demo-urbanjungle.homeadapt.us",
        "ha_webhook_id": "vapi_air_circulator",
        "name": "Urban Jungle Demo"
    },
    # Add more HA instances here:
    # "customer2": {
    #     "customer_id": "customer2",
    #     "ha_url": "https://customer2.homeadapt.us",
    #     "ha_webhook_id": "vapi_air_circulator",
    #     "name": "Customer 2 Home"
    # },
}


def get_ha_instance(customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Get HA instance configuration by customer_id.

    No password validation needed - VAPI Bearer token proves authenticity.
    """
    return HA_INSTANCES.get(customer_id)


def get_all_customers() -> list:
    """Get list of all customer IDs."""
    return list(HA_INSTANCES.keys())
