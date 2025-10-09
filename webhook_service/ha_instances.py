"""
Home Assistant Instance Configuration

Each HA instance has:
- customer_id: Unique identifier for the customer
- password: Authentication password
- ha_url: Home Assistant instance URL
- ha_webhook_id: Webhook ID for this instance
"""

from typing import Dict, Any, Optional

# Home Assistant instances configuration
# In production, load from environment variables or database
HA_INSTANCES = {
    "urbanjungle": {
        "customer_id": "urbanjungle",
        "password": "alpha-bravo-123",
        "ha_url": "https://ut-demo-urbanjungle.homeadapt.us",
        "ha_webhook_id": "vapi_air_circulator",
        "name": "Urban Jungle Demo"
    },
    # Add more HA instances here:
    # "customer2": {
    #     "customer_id": "customer2",
    #     "password": "secure-password-456",
    #     "ha_url": "https://customer2.homeadapt.us",
    #     "ha_webhook_id": "vapi_air_circulator",
    #     "name": "Customer 2 Home"
    # },
}


def get_ha_instance(customer_id: str) -> Optional[Dict[str, Any]]:
    """Get HA instance configuration by customer_id."""
    return HA_INSTANCES.get(customer_id)


def validate_credentials(customer_id: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Validate customer credentials and return HA instance config.

    Returns:
        HA instance config if valid, None otherwise
    """
    instance = get_ha_instance(customer_id)
    if not instance:
        return None

    if instance["password"] == password:
        return instance

    return None


def get_all_customers() -> list:
    """Get list of all customer IDs."""
    return list(HA_INSTANCES.keys())
