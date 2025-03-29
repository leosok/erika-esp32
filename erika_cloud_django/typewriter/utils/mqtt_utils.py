import json

import paho.mqtt.publish as publish
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


def send_mqtt_message(typewriter_uuid:str, topic: str, payload: str):
    client_id = f"{settings.MQTT_CLIENT_ID}_{typewriter_uuid}"

    # Send message
    publish.single(
        topic=topic,
        payload=payload,
        hostname=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        client_id=client_id,
        auth={'username': settings.MQTT_USER, 'password': settings.MQTT_PASS},
        qos=1,  # Ensure at least once delivery
        retain=False
    )

    logger.info(f"Successfully sent message to typewriter {typewriter_uuid} on topic {topic}")

def send_print_message(typewriter_uuid: str, text: str):
    """Send a print message to a typewriter via MQTT."""
    try:

        logger.info(f"MQTT Configuration - Host: {settings.MQTT_HOST}, Port: {settings.MQTT_PORT}, "
        f"User: {settings.MQTT_USER}, Password set: {bool(settings.MQTT_PASS)}")

        topic = f'erika/print/{typewriter_uuid}'
        send_mqtt_message(typewriter_uuid, topic, text)

        return True
    except Exception as e:
        logger.error(f"Failed to send MQTT message: {str(e)}")
        raise


def send_print_message_to_all(text: str):
    """Send a print message to all typewriters via MQTT broadcast topic"""
            
    # differnet payload for broadcast
    payload = json.dumps({
        "text": text,
        "sender": "cloud"
    })
        
    send_print_message("all", text=payload)  # Using "all" as the target will publish to erika/print/all