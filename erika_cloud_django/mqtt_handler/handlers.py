import datetime
import logging
import json
import os
from dmqtt.signals import connect, topic
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from typewriter.models import Textdata, Typewriter
#from .plugin_manager import PluginManager

# Configure logger
logger = logging.getLogger('mqtt_handler')

# Initialize plugin manager
# plugin_manager = PluginManager(os.path.join(os.path.dirname(__file__), 'plugins'))

@receiver(connect)
def on_connect(sender, **kwargs):
    logger.info(f"MQTT Configuration - Host: {settings.MQTT_HOST}, Port: {settings.MQTT_PORT}, "
            f"User: {settings.MQTT_USER}, Password set: {bool(settings.MQTT_PASS)}")

    # Connect to MQTT broker
    sender.subscribe("#")


    # topics_to_subscribe = ["#"]
    # for sub_topic in topics_to_subscribe:
    #     sender.subscribe(sub_topic)
    #     logger.info(f"MQTT Connected and subscribed to topic: {sub_topic}")

@topic("erika/print/all", as_json=False)
def simple_topic(sender, topic, msg, **kwargs):
    try:
        payload = msg.payload.decode("utf8")
        logger.info(f"MQTT message received on topic: {topic} with payload: {payload}")
    except Exception as e:
        logger.error(f"Error processing MQTT message on topic: {topic} - Error: {str(e)}")
        
@topic("erika/status/#", as_json=False)
def handle_status(sender, topic, msg, **kwargs):
    try:
        typewriter_id = topic.split('/')[2]
        status = int(msg.payload)
        logger.info(f"Status of Typewriter {typewriter_id} changed to {status}")
        try:
            typewriter = Typewriter.objects.get(uuid=typewriter_id)
            if typewriter.status < status:
                typewriter.print_mails()
            typewriter.status = status
            typewriter.save()
        except Typewriter.DoesNotExist as e:
            logger.info(e)
    except Exception as e:
        logger.error(f"Error processing status message: {str(e)}")

@topic("erika/upload/#", as_json=False)
def handle_upload(sender, topic, msg, **kwargs):
    """Handle uploaded text from typewriter."""
    try:
        payload = json.loads(msg.payload)
        logger.info(f"Upload payload: {payload}")

        typewriter_id = topic.split('/')[2]
        try:
            typewriter = Typewriter.objects.get(uuid=typewriter_id)
        except Typewriter.DoesNotExist:
            logger.error(f"Typewriter not found: {typewriter_id}")
        #     return False

        # if "cmd" in payload:
        #     # Route to appropriate plugin
        #     return plugin_manager.handle_message(
        #         command=payload["cmd"],
        #         typewriter_id=typewriter_id,
        #         payload=payload
        #     )
        # else:
        #     # Default behavior for text storage
        #     return plugin_manager.handle_message(
        #         command="store",
        #         typewriter_id=typewriter_id,
        #         payload=payload
        #     )

    except Exception as e:
        logger.error(f"Error processing upload message: {e}")
        return False
